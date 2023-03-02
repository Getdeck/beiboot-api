/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';

export class ConnectionsService {

    /**
     * Ghost Tunnel
     * @param clusterName
     * @param xForwardedUser
     * @param xForwardedGroups
     * @param xForwardedEmail
     * @param xForwardedPreferredUsername
     * @returns any Successful Response
     * @throws ApiError
     */
    public static ghostTunnelConnectionsClusterNameGhostTunnelGet(
        clusterName: any,
        xForwardedUser: string,
        xForwardedGroups?: string,
        xForwardedEmail?: string,
        xForwardedPreferredUsername?: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/connections/{cluster_name}/ghost-tunnel/',
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

}
