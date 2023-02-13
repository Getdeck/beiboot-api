/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ConfigsService {

    /**
     * Config List
     * @returns any Successful Response
     * @throws ApiError
     */
    public static configListConfigsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/configs/',
        });
    }

    /**
     * Config Default Refresh
     * @returns any Successful Response
     * @throws ApiError
     */
    public static configDefaultRefreshConfigsDefaultRefreshGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/configs/default/refresh/',
        });
    }

    /**
     * Config Refresh
     * @param name
     * @returns any Successful Response
     * @throws ApiError
     */
    public static configRefreshConfigsNameRefreshGet(
        name: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/configs/{name}/refresh/',
            path: {
                'name': name,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
