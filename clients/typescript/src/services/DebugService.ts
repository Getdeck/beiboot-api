/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DebugService {

    /**
     * Get Headers
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getHeadersDebugHeadersGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/debug/headers',
        });
    }

    /**
     * Trigger Error
     * @returns any Successful Response
     * @throws ApiError
     */
    public static triggerErrorDebugSentryGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/debug/sentry',
        });
    }

}
