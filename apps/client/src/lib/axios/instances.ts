import axios from 'axios';
import { getApiBaseUrl } from '../../config/api';
import {
  attachPrivateRequestInterceptor,
  attachPrivateResponseInterceptor,
} from './interceptors';

const baseConfig = {
  baseURL: getApiBaseUrl(),
  timeout: 20_000,
  withCredentials: true,
  headers: {
    Accept: 'application/json',
  },
};

/** Public client for authentication and endpoints without private retry logic. */
export const axiosPublicInstance = axios.create(baseConfig);

/** Private client that authenticates exclusively through HttpOnly cookies. */
export const axiosPrivateInstance = axios.create(baseConfig);

attachPrivateRequestInterceptor(axiosPrivateInstance);
attachPrivateResponseInterceptor(axiosPrivateInstance, axiosPublicInstance);
