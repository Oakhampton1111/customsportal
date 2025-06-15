async function globalTeardown() {
  console.log('🧹 Starting global teardown for Playwright E2E tests...');
  
  try {
    // Perform any global cleanup tasks
    console.log('🔧 Performing global cleanup tasks...');
    
    // Clean up any test artifacts, temporary files, etc.
    // This could include:
    // - Clearing test databases
    // - Removing temporary files
    // - Cleaning up test data
    // - Resetting application state
    
    // Log test completion statistics
    console.log('📊 Test execution completed');
    console.log('📁 Test results saved to: test-results/');
    
    // Clean up any remaining browser processes (safety measure)
    // Note: Playwright usually handles this automatically
    
    console.log('✅ Global teardown completed successfully');
    
  } catch (error) {
    console.error('❌ Global teardown failed:', error);
    // Don't throw here as it might mask test failures
  }
}

export default globalTeardown;