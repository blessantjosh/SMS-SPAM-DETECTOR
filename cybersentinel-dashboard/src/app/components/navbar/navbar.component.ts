import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { ApiService, SystemStatusResponse } from '../../services/api.service';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [CommonModule, RouterLink, RouterLinkActive],
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.scss']
})
export class NavbarComponent implements OnInit {
  systemStatus: SystemStatusResponse | null = null;
  isMenuOpen = false;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadSystemStatus();
    // Refresh status every 30 seconds
    setInterval(() => this.loadSystemStatus(), 30000);
  }

  loadSystemStatus() {
    this.apiService.getSystemStatus().subscribe({
      next: (status) => {
        this.systemStatus = status;
      },
      error: (err) => {
        console.error('Failed to load system status:', err);
      }
    });
  }

  toggleMenu() {
    this.isMenuOpen = !this.isMenuOpen;
  }
}
