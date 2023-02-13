/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class DefaultService {

    /**
     * Get Root
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getRootGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/',
        });
    }

    /**
     * Trigger Error
     * @returns any Successful Response
     * @throws ApiError
     */
    public static triggerErrorSentryDebugGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/sentry-debug/',
        });
    }

}
