import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { ApiService, SMSAnalyzeResponse } from '../../services/api.service';

@Component({
  selector: 'app-sms-detection',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './sms-detection.component.html',
  styleUrls: ['./sms-detection.component.scss']
})
export class SmsDetectionComponent {
  smsMessage = '';
  analyzing = false;
  result: SMSAnalyzeResponse | null = null;
  error: string | null = null;

  exampleMessages = [
    'URGENT: Your bank account will be blocked within 24 hours. Click http://bit.ly/verifykyc to update your KYC details immediately!',
    'Your mobile recharge of Rs 499 was successful. Thank you for using our service.',
    'You have won Rs 50000 in Jio lucky draw. Pay processing fee of Rs 500 to claim: bit.ly/claim123',
    'Dear customer, your electricity bill of Rs 1200 is due on 25th Nov. Pay online at www.officialwebsite.com'
  ];

  constructor(private apiService: ApiService) {}

  analyzeSMS() {
    if (!this.smsMessage.trim()) {
      this.error = 'Please enter an SMS message to analyze';
      return;
    }

    this.analyzing = true;
    this.error = null;
    this.result = null;

    this.apiService.analyzeSMS(this.smsMessage).subscribe({
      next: (response) => {
        this.result = response;
        this.analyzing = false;
      },
      error: (err) => {
        console.error('Analysis failed:', err);
        this.error = 'Failed to analyze SMS. Please ensure the backend server is running.';
        this.analyzing = false;
      }
    });
  }

  loadExample(message: string) {
    this.smsMessage = message;
    this.result = null;
    this.error = null;
  }

  clear() {
    this.smsMessage = '';
    this.result = null;
    this.error = null;
  }

  get charCount(): number {
    return this.smsMessage.length;
  }

  get isScam(): boolean {
    return this.result?.prediction === 'SCAM';
  }

  get isLegitimate(): boolean {
    return this.result?.prediction === 'LEGITIMATE';
  }

  get riskColor(): string {
    if (!this.result) return '';

    switch (this.result.risk_category) {
      case 'high':
        return 'red';
      case 'medium':
        return 'yellow';
      case 'low':
        return 'green';
      default:
        return 'gray';
    }
  }
}
