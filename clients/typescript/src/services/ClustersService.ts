/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BeibootRequest } from '../models/BeibootRequest';
import type { BeibootResponse } from '../models/BeibootResponse';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ClustersService {

    /**
     * Cluster List
     * @param userId
     * @returns BeibootResponse Successful Response
     * @throws ApiError
     */
    public static clusterListClustersGet(
        userId: string = 'default',
    ): CancelablePromise<Array<BeibootResponse>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/',
            headers: {
                'user-id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Cluster Create
     * @param requestBody
     * @param userId
     * @returns BeibootResponse Successful Response
     * @throws ApiError
     */
    public static clusterCreateClustersPost(
        requestBody: BeibootRequest,
        userId: string = 'default',
    ): CancelablePromise<BeibootResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/clusters/',
            headers: {
                'user-id': userId,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Cluster Delete
     * @param name
     * @param userId
     * @returns BeibootResponse Successful Response
     * @throws ApiError
     */
    public static clusterDeleteClustersNameDelete(
        name: string,
        userId: string = 'default',
    ): CancelablePromise<BeibootResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/clusters/{name}',
            path: {
                'name': name,
            },
            headers: {
                'user-id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Cluster State
     * @param name
     * @param userId
     * @returns BeibootResponse Successful Response
     * @throws ApiError
     */
    public static clusterStateClustersNameStateGet(
        name: string,
        userId: string = 'default',
    ): CancelablePromise<BeibootResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/{name}/state',
            path: {
                'name': name,
            },
            headers: {
                'user-id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Cluster Kubeconfig
     * @param name
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static clusterKubeconfigClustersNameKubeconfigGet(
        name: string,
        userId: string = 'default',
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/{name}/kubeconfig',
            path: {
                'name': name,
            },
            headers: {
                'user-id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Cluster Mtls
     * @param name
     * @param userId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static clusterMtlsClustersNameMtlsGet(
        name: string,
        userId: string = 'default',
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/{name}/mtls',
            path: {
                'name': name,
            },
            headers: {
                'user-id': userId,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
