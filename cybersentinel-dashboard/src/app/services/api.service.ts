import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface SMSAnalyzeRequest {
  message: string;
}

export interface SMSAnalyzeResponse {
  sms: string;
  prediction: string;
  label: string;
  model_name: string;
  inference_time_ms: number;
  probabilities?: {
    ham: number;
    scam: number;
  };
  confidence?: number;
  risk_category: string;
  recommendation: string;
  timestamp: string;
}

export interface SystemStatusResponse {
  status: string;
  model_loaded: boolean;
  model_name?: string;
  model_path?: string;
  backend_version: string;
  timestamp: string;
}

export interface ModelPerformance {
  model_name: string;
  test_accuracy: number;
  f1_scam: number;
  f1_ham: number;
  macro_f1: number;
  precision_scam: number;
  recall_scam: number;
  false_positive_rate: number;
  false_negative_rate: number;
}

export interface DashboardStats {
  total_analyzed: number;
  scam_detected: number;
  legitimate_detected: number;
  suspicious_detected: number;
  model_name: string;
  last_updated: string;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  /**
   * Get system status
   */
  getSystemStatus(): Observable<SystemStatusResponse> {
    return this.http.get<SystemStatusResponse>(`${this.baseUrl}/system/status`);
  }

  /**
   * Analyze SMS message
   */
  analyzeSMS(message: string): Observable<SMSAnalyzeResponse> {
    return this.http.post<SMSAnalyzeResponse>(
      `${this.baseUrl}/sms/analyze`,
      { message }
    );
  }

  /**
   * Get model performance metrics
   */
  getModelPerformance(): Observable<ModelPerformance> {
    return this.http.get<ModelPerformance>(`${this.baseUrl}/model/performance`);
  }

  /**
   * Get dashboard statistics
   */
  getDashboardStats(): Observable<DashboardStats> {
    return this.http.get<DashboardStats>(`${this.baseUrl}/dashboard/stats`);
  }
}
