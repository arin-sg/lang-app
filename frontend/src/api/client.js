/**
 * API Client for backend communication
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Ingest German text and extract learnable items
 * @param {string} text - German text to analyze
 * @returns {Promise} - Extraction results
 */
export const ingestText = async (text) => {
  const response = await apiClient.post('/sources', { text });
  return response.data;
};

/**
 * Get today's review deck
 * @param {number} limit - Maximum items to return
 * @returns {Promise} - Review deck
 */
export const getReviewDeck = async (limit = 20) => {
  const response = await apiClient.get('/review/today', { params: { limit } });
  return response.data;
};

/**
 * Submit review result
 * @param {object} result - Review result data
 * @returns {Promise} - Confirmation
 */
export const submitReviewResult = async (result) => {
  const response = await apiClient.post('/review/result', result);
  return response.data;
};

/**
 * Check system health
 * @returns {Promise} - Health status
 */
export const checkHealth = async () => {
  const response = await apiClient.get('/health');
  return response.data;
};

/**
 * Get library items with optional filtering
 * @param {string} typeFilter - Filter by type (word, chunk, pattern)
 * @param {number} limit - Maximum items to return
 * @param {number} offset - Number of items to skip
 * @returns {Promise} - Library items
 */
export const getLibraryItems = async (typeFilter = null, limit = 50, offset = 0) => {
  const params = { limit, offset };
  if (typeFilter && typeFilter !== 'all') {
    params.type_filter = typeFilter;
  }
  const response = await apiClient.get('/library/items', { params });
  return response.data;
};

/**
 * Get detailed information for a specific item
 * @param {number} itemId - ID of the item
 * @returns {Promise} - Item details with relationships
 */
export const getItemDetail = async (itemId) => {
  const response = await apiClient.get(`/library/items/${itemId}`);
  return response.data;
};

/**
 * Delete one or more items
 * @param {number[]} itemIds - Array of item IDs to delete
 * @returns {Promise} - Deletion result with statistics
 */
export const deleteItems = async (itemIds) => {
  const response = await apiClient.post('/library/delete', {
    item_ids: itemIds
  });
  return response.data;
};

export default apiClient;
