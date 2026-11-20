import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService, ModelPerformance } from '../../services/api.service';

@Component({
  selector: 'app-model-performance',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './model-performance.component.html',
  styleUrls: ['./model-performance.component.scss']
})
export class ModelPerformanceComponent implements OnInit {
  performance: ModelPerformance | null = null;
  loading = true;
  error: string | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadPerformance();
  }

  loadPerformance() {
    this.loading = true;
    this.error = null;

    this.apiService.getModelPerformance().subscribe({
      next: (performance) => {
        this.performance = performance;
        this.loading = false;
      },
      error: (err) => {
        console.error('Failed to load model performance:', err);
        this.error = 'Failed to load model performance. Please ensure the backend server is running.';
        this.loading = false;
      }
    });
  }

  getPerformanceColor(value: number, inverse: boolean = false): string {
    if (inverse) {
      // For error rates - lower is better
      if (value <= 0.05) return 'text-green-400';
      if (value <= 0.1) return 'text-yellow-400';
      return 'text-red-400';
    } else {
      // For accuracy/precision/recall - higher is better
      if (value >= 0.9) return 'text-green-400';
      if (value >= 0.7) return 'text-yellow-400';
      return 'text-red-400';
    }
  }

  getPerformanceBgColor(value: number, inverse: boolean = false): string {
    if (inverse) {
      if (value <= 0.05) return 'bg-green-500/20';
      if (value <= 0.1) return 'bg-yellow-500/20';
      return 'bg-red-500/20';
    } else {
      if (value >= 0.9) return 'bg-green-500/20';
      if (value >= 0.7) return 'bg-yellow-500/20';
      return 'bg-red-500/20';
    }
  }

  formatPercentage(value: number): string {
    return (value * 100).toFixed(2) + '%';
  }
}
