/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { IntegerParameter } from './IntegerParameter';
import type { StringParameter } from './StringParameter';

export type ClusterRequest = {
    name: string;
    parameters?: Array<(StringParameter | IntegerParameter)>;
    ports?: Array<string>;
    labels?: Record<string, string>;
};

