"""
GRPO (Group Relative Policy Optimization) Trainer for CivicMind

This module implements LLM-based reinforcement learning using GRPO algorithm.
GRPO generates multiple samples per prompt, computes rewards, and updates the policy
to favor high-reward responses.
"""

import os
import time
import torch
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from tqdm import tqdm
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
    Trainer
)
from peft import LoraConfig, get_peft_model, TaskType
import numpy as np


class GRPOTrainer:
    """
    GRPO Trainer for LLM-based reinforcement learning.
    
    Uses LoRA adapters for efficient fine-tuning and implements GRPO algorithm
    for policy optimization based on text-based reward signals.
    """
    
    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-0.5B-Instruct",
        epochs: int = 3,
        batch_size: int = 2,
        n_samples_per_prompt: int = 4,
        learning_rate: float = 5e-5,
        max_length: int = 256,
        device: Optional[str] = None,
        use_fp16: bool = True
    ):
        """
        Initialize GRPO Trainer.
        
        Args:
            model_name: HuggingFace model identifier
            epochs: Number of training epochs
            batch_size: Batch size for training
            n_samples_per_prompt: Number of samples to generate per prompt for GRPO
            learning_rate: Learning rate for optimizer
            max_length: Maximum sequence length
            device: Device to use (cuda/cpu), auto-detected if None
            use_fp16: Whether to use mixed precision training
        """
        self.model_name = model_name
        self.epochs = epochs
        self.batch_size = batch_size
        self.n_samples_per_prompt = n_samples_per_prompt
        self.learning_rate = learning_rate
        self.max_length = max_length
        self.use_fp16 = use_fp16
        
        # Auto-detect device if not specified
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        # Model and tokenizer (loaded lazily)
        self.model = None
        self.tokenizer = None
        self.original_model = None
        
        # Training statistics
        self.training_stats = {
            'losses': [],
            'rewards': [],
            'epoch_times': [],
            'total_time': 0
        }
    
    def load_model(self) -> None:
        """
        Load model and tokenizer with LoRA adapters.
        
        Configures LoRA with:
        - r=16 (rank)
        - alpha=32 (scaling factor)
        - dropout=0.05
        - target_modules: q_proj, k_proj, v_proj, o_proj
        """
        print(f"📥 Loading model: {self.model_name}")
        print(f"   Device: {self.device}")
        print(f"   Mixed Precision (fp16): {self.use_fp16}")
        print()
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        
        # Set padding token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load base model
        dtype = torch.float16 if self.use_fp16 and self.device.type == "cuda" else torch.float32
        
        self.original_model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=dtype,
            trust_remote_code=True,
            device_map="auto" if self.device.type == "cuda" else None
        )
        
        if self.device.type == "cpu":
            self.original_model = self.original_model.to(self.device)
        
        # Configure LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,
            r=16,  # Rank
            lora_alpha=32,  # Scaling factor
            lora_dropout=0.05,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
            bias="none"
        )
        
        # Apply LoRA to model
        self.model = get_peft_model(self.original_model, lora_config)
        
        # Print trainable parameters
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        
        print(f"✅ Model loaded successfully!")
        print(f"   Total parameters: {total_params:,}")
        print(f"   Trainable parameters: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
        print(f"   LoRA config: r=16, alpha=32, dropout=0.05")
        print()
    
    def compute_text_reward(self, prompt: str, response: str) -> float:
        """
        Compute reward for a text response using reward shaping.
        
        Positive rewards for:
        - Welfare investment keywords
        - Trust building actions
        - Crisis response actions
        
        Negative rewards for:
        - Force/riot control
        - Inaction during crisis
        - Tax increases during low trust
        
        Args:
            prompt: Input prompt
            response: Generated response
            
        Returns:
            Reward score (float)
        """
        response_lower = response.lower()
        reward = 0.0
        
        # Positive reward keywords
        positive_keywords = [
            'welfare', 'invest', 'trust', 'community', 'support',
            'help', 'assist', 'improve', 'crisis response', 'emergency',
            'healthcare', 'education', 'infrastructure', 'transparency'
        ]
        
        # Negative reward keywords
        negative_keywords = [
            'force', 'riot control', 'suppress', 'ignore', 'inaction',
            'tax increase', 'cut budget', 'reduce spending', 'do nothing'
        ]
        
        # Count positive keywords
        for keyword in positive_keywords:
            if keyword in response_lower:
                reward += 0.5
        
        # Count negative keywords
        for keyword in negative_keywords:
            if keyword in response_lower:
                reward -= 0.5
        
        # Bonus for longer, more detailed responses (up to a point)
        response_length = len(response.split())
        if 10 <= response_length <= 50:
            reward += 0.2
        elif response_length > 100:
            reward -= 0.1  # Penalize overly verbose responses
        
        return reward
    
    def generate_samples(
        self,
        prompt: str,
        n_samples: int,
        temperature: float = 0.8,
        top_p: float = 0.9
    ) -> List[str]:
        """
        Generate multiple samples for a given prompt.
        
        Args:
            prompt: Input prompt
            n_samples: Number of samples to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            
        Returns:
            List of generated text samples
        """
        # Tokenize prompt
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=self.max_length
        ).to(self.device)
        
        samples = []
        
        # Generate samples
        with torch.no_grad():
            for _ in range(n_samples):
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=128,
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
                
                # Decode output
                generated_text = self.tokenizer.decode(
                    outputs[0][inputs['input_ids'].shape[1]:],
                    skip_special_tokens=True
                )
                samples.append(generated_text)
        
        return samples
    
    def grpo_step(
        self,
        prompts: List[str],
        optimizer: torch.optim.Optimizer
    ) -> Tuple[float, float]:
        """
        Perform one GRPO training step.
        
        For each prompt:
        1. Generate N samples
        2. Compute rewards for each sample
        3. Select best sample based on reward
        4. Update policy to increase probability of best sample
        
        Args:
            prompts: List of training prompts
            optimizer: Optimizer instance
            
        Returns:
            Tuple of (average_loss, average_reward)
        """
        self.model.train()
        total_loss = 0.0
        total_reward = 0.0
        
        for prompt in prompts:
            # Generate multiple samples
            samples = self.generate_samples(prompt, self.n_samples_per_prompt)
            
            # Compute rewards for each sample
            rewards = [self.compute_text_reward(prompt, sample) for sample in samples]
            
            # Select best sample
            best_idx = np.argmax(rewards)
            best_sample = samples[best_idx]
            best_reward = rewards[best_idx]
            
            # Prepare training data (prompt + best response)
            full_text = prompt + best_sample
            
            # Tokenize
            inputs = self.tokenizer(
                full_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.max_length
            ).to(self.device)
            
            # Forward pass
            outputs = self.model(**inputs, labels=inputs['input_ids'])
            loss = outputs.loss
            
            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            total_reward += best_reward
        
        avg_loss = total_loss / len(prompts)
        avg_reward = total_reward / len(prompts)
        
        return avg_loss, avg_reward
    
    def train(self, training_prompts: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Train the model using GRPO algorithm.
        
        Args:
            training_prompts: List of training prompts. If None, uses default prompts.
            
        Returns:
            Dictionary of training statistics
        """
        # Load model if not already loaded
        if self.model is None:
            self.load_model()
        
        # Use default prompts if none provided
        if training_prompts is None:
            training_prompts = self._get_default_prompts()
        
        print(f"🚀 Starting GRPO Training")
        print(f"   Epochs: {self.epochs}")
        print(f"   Batch size: {self.batch_size}")
        print(f"   Samples per prompt: {self.n_samples_per_prompt}")
        print(f"   Training prompts: {len(training_prompts)}")
        print(f"   Learning rate: {self.learning_rate}")
        print()
        
        # Setup optimizer
        optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.learning_rate
        )
        
        # Training loop
        start_time = time.time()
        
        for epoch in range(self.epochs):
            epoch_start = time.time()
            epoch_losses = []
            epoch_rewards = []
            
            # Create progress bar
            pbar = tqdm(
                range(0, len(training_prompts), self.batch_size),
                desc=f"Epoch {epoch + 1}/{self.epochs}"
            )
            
            for i in pbar:
                # Get batch
                batch_prompts = training_prompts[i:i + self.batch_size]
                
                # GRPO step
                loss, reward = self.grpo_step(batch_prompts, optimizer)
                
                epoch_losses.append(loss)
                epoch_rewards.append(reward)
                
                # Update progress bar
                pbar.set_postfix({
                    'loss': f'{loss:.4f}',
                    'reward': f'{reward:.4f}'
                })
            
            epoch_time = time.time() - epoch_start
            
            # Store epoch statistics
            avg_epoch_loss = np.mean(epoch_losses)
            avg_epoch_reward = np.mean(epoch_rewards)
            
            self.training_stats['losses'].extend(epoch_losses)
            self.training_stats['rewards'].extend(epoch_rewards)
            self.training_stats['epoch_times'].append(epoch_time)
            
            print(f"\n📊 Epoch {epoch + 1} Summary:")
            print(f"   Average Loss: {avg_epoch_loss:.4f}")
            print(f"   Average Reward: {avg_epoch_reward:.4f}")
            print(f"   Epoch Time: {epoch_time:.2f}s")
            print()
        
        total_time = time.time() - start_time
        self.training_stats['total_time'] = total_time
        
        print(f"✅ Training Complete!")
        print(f"   Total Time: {total_time:.2f}s ({total_time/60:.2f} min)")
        print(f"   Final Loss: {self.training_stats['losses'][-1]:.4f}")
        print(f"   Final Reward: {self.training_stats['rewards'][-1]:.4f}")
        print()
        
        return self.training_stats
    
    def _get_default_prompts(self) -> List[str]:
        """
        Get default training prompts for CivicMind agents.
        
        Returns:
            List of training prompts
        """
        prompts = [
            "As mayor, the city faces a budget crisis. What action should you take?",
            "Public trust is low and there are protests. How do you respond?",
            "A health crisis has emerged. What is your immediate action?",
            "The economy is struggling. What policy do you implement?",
            "Crime rates are rising. What is your approach?",
            "Infrastructure is failing. How do you address this?",
            "Media is reporting negative stories. How do you respond?",
            "A natural disaster has occurred. What is your crisis response?",
            "Citizens are demanding more transparency. What do you do?",
            "Budget surplus is available. How do you allocate it?",
            "Rebel activity is increasing. What is your strategy?",
            "Education system needs improvement. What action do you take?",
            "Healthcare costs are rising. How do you manage this?",
            "Public services are underfunded. What is your priority?",
            "Environmental concerns are growing. How do you respond?",
            "Social inequality is widening. What policy do you propose?",
            "Technology infrastructure needs upgrading. What do you invest in?",
            "Community engagement is low. How do you improve it?",
            "Emergency services are stretched. What do you do?",
            "Long-term planning is needed. What is your vision?"
        ]
        return prompts
    
    def save_checkpoint(self, save_path: str) -> None:
        """
        Save model checkpoint and training statistics.
        
        Args:
            save_path: Directory path to save checkpoint
        """
        save_path = Path(save_path)
        save_path.mkdir(parents=True, exist_ok=True)
        
        print(f"💾 Saving checkpoint to: {save_path}")
        
        # Save model and tokenizer
        self.model.save_pretrained(save_path)
        self.tokenizer.save_pretrained(save_path)
        
        # Save training statistics
        stats_path = save_path / "training_stats.json"
        with open(stats_path, 'w') as f:
            json.dump(self.training_stats, f, indent=2)
        
        print(f"   ✅ Model saved")
        print(f"   ✅ Tokenizer saved")
        print(f"   ✅ Training stats saved")
        print()
    
    def load_checkpoint(self, load_path: str) -> None:
        """
        Load model checkpoint.
        
        Args:
            load_path: Directory path to load checkpoint from
        """
        load_path = Path(load_path)
        
        print(f"📥 Loading checkpoint from: {load_path}")
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(load_path)
        
        # Load model
        dtype = torch.float16 if self.use_fp16 and self.device.type == "cuda" else torch.float32
        
        self.model = AutoModelForCausalLM.from_pretrained(
            load_path,
            torch_dtype=dtype,
            device_map="auto" if self.device.type == "cuda" else None
        )
        
        if self.device.type == "cpu":
            self.model = self.model.to(self.device)
        
        # Load training statistics if available
        stats_path = load_path / "training_stats.json"
        if stats_path.exists():
            with open(stats_path, 'r') as f:
                self.training_stats = json.load(f)
        
        print(f"   ✅ Checkpoint loaded successfully")
        print()
    
    def plot_training_curve(self, save_path: Optional[str] = None, show: bool = True) -> None:
        """
        Plot training loss and reward curves.
        
        Args:
            save_path: Path to save plot (optional)
            show: Whether to display plot
        """
        try:
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
            
            # Plot loss
            ax1.plot(self.training_stats['losses'], label='Loss', color='red', alpha=0.7)
            ax1.set_xlabel('Training Step')
            ax1.set_ylabel('Loss')
            ax1.set_title('GRPO Training Loss')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            # Plot reward
            ax2.plot(self.training_stats['rewards'], label='Reward', color='green', alpha=0.7)
            ax2.set_xlabel('Training Step')
            ax2.set_ylabel('Reward')
            ax2.set_title('GRPO Training Reward')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"📊 Training curve saved to: {save_path}")
            
            if show:
                plt.show()
            else:
                plt.close()
                
        except ImportError:
            print("⚠️  matplotlib not available, skipping plot generation")
