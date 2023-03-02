/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ClusterRequest } from '../models/ClusterRequest';
import type { ClusterResponse } from '../models/ClusterResponse';
import type { Page_ClusterResponse_ } from '../models/Page_ClusterResponse_';
import type { Page_dict_ } from '../models/Page_dict_';

import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ClustersService {

    /**
     * Get
     * @param xForwardedUser
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getClustersWsGet(
        xForwardedUser: string,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/ws',
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
     * Cluster List
     * @param xForwardedUser
     * @param page
     * @param size
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns Page_ClusterResponse_ Successful Response
     * @throws ApiError
     */
    public static clusterListClustersGet(
        xForwardedUser: string,
        page: number = 1,
        size: number = 50,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<Page_ClusterResponse_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/',
            headers: {
                'x-forwarded-user': xForwardedUser,
                'x-forwarded-groups': xForwardedGroups,
                'x-forwarded-email': xForwardedEmail,
                'x-forwarded-preferred-username': xForwardedPreferredUsername,
            },
            query: {
                'page': page,
                'size': size,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Cluster Create
     * @param xForwardedUser
     * @param requestBody
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns ClusterResponse Successful Response
     * @throws ApiError
     */
    public static clusterCreateClustersPost(
        xForwardedUser: string,
        requestBody: ClusterRequest,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<ClusterResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/clusters/',
            headers: {
                'x-forwarded-user': xForwardedUser,
                'x-forwarded-groups': xForwardedGroups,
                'x-forwarded-email': xForwardedEmail,
                'x-forwarded-preferred-username': xForwardedPreferredUsername,
            },
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Cluster Info
     * @param clusterName
     * @param xForwardedUser
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns ClusterResponse Successful Response
     * @throws ApiError
     */
    public static clusterInfoClustersClusterNameGet(
        clusterName: string,
        xForwardedUser: string,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<ClusterResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/{cluster_name}',
            path: {
                'cluster_name': clusterName,
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

    /**
     * Cluster Delete
     * @param clusterName
     * @param xForwardedUser
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns ClusterResponse Successful Response
     * @throws ApiError
     */
    public static clusterDeleteClustersClusterNameDelete(
        clusterName: string,
        xForwardedUser: string,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<ClusterResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/clusters/{cluster_name}',
            path: {
                'cluster_name': clusterName,
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

    /**
     * Cluster State
     * @param clusterName
     * @param xForwardedUser
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns ClusterResponse Successful Response
     * @throws ApiError
     */
    public static clusterStateClustersClusterNameHeartbeatGet(
        clusterName: string,
        xForwardedUser: string,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<ClusterResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/{cluster_name}/heartbeat',
            path: {
                'cluster_name': clusterName,
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

    /**
     * Cluster Kubeconfig
     * @param clusterName
     * @param xForwardedUser
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns any Successful Response
     * @throws ApiError
     */
    public static clusterKubeconfigClustersClusterNameKubeconfigGet(
        clusterName: string,
        xForwardedUser: string,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/{cluster_name}/kubeconfig',
            path: {
                'cluster_name': clusterName,
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

    /**
     * Cluster Parameters
     * @param clusterName
     * @param xForwardedUser
     * @param page
     * @param size
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns Page_dict_ Successful Response
     * @throws ApiError
     */
    public static clusterParametersClustersClusterNameParametersGet(
        clusterName: string,
        xForwardedUser: string,
        page: number = 1,
        size: number = 50,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<Page_dict_> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/{cluster_name}/parameters',
            path: {
                'cluster_name': clusterName,
            },
            headers: {
                'x-forwarded-user': xForwardedUser,
                'x-forwarded-groups': xForwardedGroups,
                'x-forwarded-email': xForwardedEmail,
                'x-forwarded-preferred-username': xForwardedPreferredUsername,
            },
            query: {
                'page': page,
                'size': size,
            },
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Cluster Parameter
     * @param clusterName
     * @param parameterName
     * @param xForwardedUser
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns any Successful Response
     * @throws ApiError
     */
    public static clusterParameterClustersClusterNameParametersParameterNameGet(
        clusterName: string,
        parameterName: string,
        xForwardedUser: string,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/clusters/{cluster_name}/parameters/{parameter_name}',
            path: {
                'cluster_name': clusterName,
                'parameter_name': parameterName,
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
