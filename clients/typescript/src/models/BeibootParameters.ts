/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type BeibootParameters = {
    k8sVersion?: string;
    ports?: Array<string>;
    nodes?: number;
    maxLifetime?: string;
    maxSessionTimeout?: string;
    serverResources?: Record<string, Record<string, string>>;
    nodeResources?: Record<string, Record<string, string>>;
    serverStorageRequests?: string;
    nodeStorageRequests?: string;
};

