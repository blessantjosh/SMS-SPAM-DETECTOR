import { Routes } from '@angular/router';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { SmsDetectionComponent } from './components/sms-detection/sms-detection.component';
import { ModelPerformanceComponent } from './components/model-performance/model-performance.component';

export const routes: Routes = [
  { path: '', component: DashboardComponent },
  { path: 'sms-detection', component: SmsDetectionComponent },
  { path: 'model-performance', component: ModelPerformanceComponent },
  { path: '**', redirectTo: '' }
];
