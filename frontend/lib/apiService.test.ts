/**
 * Test file demonstrating API service usage
 * This file shows how the API service would be tested in a real implementation
 */

import { apiService } from './apiService';

// Mock test to show intended usage (actual testing would require Jest or similar)
describe('ApiService', () => {
  // These would be actual tests in a real implementation
  test('should be able to instantiate the service', () => {
    expect(apiService).toBeDefined();
  });

  test('healthCheck method should exist', () => {
    expect(typeof apiService.healthCheck).toBe('function');
  });

  test('getAssetHealth method should exist', () => {
    expect(typeof apiService.getAssetHealth).toBe('function');
  });

  // Additional method existence tests would go here
});

/**
 * Example of how to use the API service in a component:
 *
 * import { useEffect, useState } from 'react';
 * import { apiService } from '@/lib/apiService';
 *
 * function MyComponent() {
 *   const [data, setData] = useState(null);
 *   const [loading, setLoading] = useState(false);
 *
 *   useEffect(() => {
 *     const fetchData = async () => {
 *       try {
 *         setLoading(true);
 *         const result = await apiService.getAssetSummary('T-01');
 *         setData(result);
 *       } catch (error) {
 *         console.error('Failed to fetch data:', error);
 *       } finally {
 *         setLoading(false);
 *       }
 *     };
 *
 *     fetchData();
 *   }, []);
 *
 *   // Render component with data, loading, and error states
 * }
 */
export {};