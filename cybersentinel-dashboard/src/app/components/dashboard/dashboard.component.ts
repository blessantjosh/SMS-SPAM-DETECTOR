import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService, DashboardStats, SystemStatusResponse } from '../../services/api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  stats: DashboardStats | null = null;
  systemStatus: SystemStatusResponse | null = null;
  loading = false;
  error: string | null = null;
  dataLoaded = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    // Don't load data automatically - wait for user action
    // this.loadData();
  }

  loadData() {
    this.loading = true;
    this.error = null;

    // Load system status
    this.apiService.getSystemStatus().subscribe({
      next: (status) => {
        this.systemStatus = status;
      },
      error: (err) => {
        console.error('Failed to load system status:', err);
        this.error = 'Backend API is not available. Please start the FastAPI server.';
        this.loading = false;
      }
    });

    // Load dashboard stats
    this.apiService.getDashboardStats().subscribe({
      next: (stats) => {
        this.stats = stats;
        this.loading = false;
        this.dataLoaded = true;
      },
      error: (err) => {
        console.error('Failed to load stats:', err);
        this.error = 'Failed to load dashboard statistics. Please try again.';
        this.loading = false;
      }
    });
  }

  refreshData() {
    this.loadData();
  }

  get scamPercentage(): number {
    if (!this.stats || this.stats.total_analyzed === 0) return 0;
    return (this.stats.scam_detected / this.stats.total_analyzed) * 100;
  }

  get hamPercentage(): number {
    if (!this.stats || this.stats.total_analyzed === 0) return 0;
    return (this.stats.legitimate_detected / this.stats.total_analyzed) * 100;
  }

  get totalAnalyzed(): number {
    return this.stats?.total_analyzed || 0;
  }

  get scamDetected(): number {
    return this.stats?.scam_detected || 0;
  }

  get legitimateDetected(): number {
    return this.stats?.legitimate_detected || 0;
  }

  get suspiciousDetected(): number {
    return this.stats?.suspicious_detected || 0;
  }
}
