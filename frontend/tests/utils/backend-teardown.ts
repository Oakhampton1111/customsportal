/**
 * Global teardown for integration tests - stops backend server and cleans up
 */

import { backendProcess } from './backend-setup';

/**
 * Global teardown function called by Jest
 */
export default async function globalTeardown(): Promise<void> {
  console.log('🧹 Cleaning up integration test environment...');
  
  try {
    // Stop backend server
    if (backendProcess) {
      console.log('🛑 Stopping backend server...');
      backendProcess.kill('SIGTERM');
      
      // Wait for graceful shutdown
      await new Promise<void>((resolve) => {
        if (backendProcess) {
          backendProcess.on('exit', () => {
            console.log('✓ Backend server stopped');
            resolve();
          });
          
          // Force kill after timeout
          setTimeout(() => {
            if (backendProcess && !backendProcess.killed) {
              backendProcess.kill('SIGKILL');
              console.log('✓ Backend server force stopped');
              resolve();
            }
          }, 5000);
        } else {
          resolve();
        }
      });
    }
    
    // Clean up environment variables
    delete process.env.INTEGRATION_BACKEND_URL;
    
    console.log('✅ Integration test environment cleaned up');
    
  } catch (error) {
    console.error('❌ Error during teardown:', error);
  }
}