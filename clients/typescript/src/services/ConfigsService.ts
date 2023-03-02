/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ConfigsService {

    /**
     * Config List
     * @param xForwardedUser
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns any Successful Response
     * @throws ApiError
     */
    public static configListConfigsGet(
        xForwardedUser: string,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/configs/',
            headers: {
                'x-forwarded-user': xForwardedUser,
                'x-forwarded-groups': xForwardedGroups,
                'x-forwarded-email': xForwardedEmail,
                'x-forwarded-preferred-username': xForwardedPreferredUsername,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Config Default Refresh
     * @param xForwardedUser
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns any Successful Response
     * @throws ApiError
     */
    public static configDefaultRefreshConfigsDefaultRefreshGet(
        xForwardedUser: string,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/configs/default/refresh/',
            headers: {
                'x-forwarded-user': xForwardedUser,
                'x-forwarded-groups': xForwardedGroups,
                'x-forwarded-email': xForwardedEmail,
                'x-forwarded-preferred-username': xForwardedPreferredUsername,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Config Refresh
     * @param configName
     * @param xForwardedUser
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns any Successful Response
     * @throws ApiError
     */
    public static configRefreshConfigsConfigNameRefreshGet(
        configName: string,
        xForwardedUser: string,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/configs/{config_name}/refresh/',
            path: {
                'config_name': configName,
            },
            headers: {
                'x-forwarded-user': xForwardedUser,
                'x-forwarded-groups': xForwardedGroups,
                'x-forwarded-email': xForwardedEmail,
                'x-forwarded-preferred-username': xForwardedPreferredUsername,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
