/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { BeibootParameters } from './BeibootParameters';
import type { BeibootProvider } from './BeibootProvider';

export type BeibootRequest = {
    name: string;
    provider?: BeibootProvider;
    parameters?: BeibootParameters;
    labels?: Record<string, string>;
};

