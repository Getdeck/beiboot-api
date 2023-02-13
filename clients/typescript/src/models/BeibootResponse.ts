/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BeibootState } from './BeibootState';

export type BeibootResponse = {
    name: string;
    state: BeibootState;
    mtls_files?: any;
};

