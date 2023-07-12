/**
 * Will deploy into the current default CLI account.
 *
 * Deployment:
 * cdk deploy --all
 */

/* eslint-disable no-new */
import 'source-map-support/register';
import { App } from 'aws-cdk-lib';
import { SnsConfigStack } from '../lib/sns-config-stack';

const app = new App();

// Use account details from default AWS CLI credentials:
const account = '395929101814';
const region = 'us-east-2';
const env = { account, region };

// Create SNS Configuration Stack
new SnsConfigStack(app, 'SnsConfigStack', {
    description: 'SNS SMS Configuration Stack',
    env,
});
