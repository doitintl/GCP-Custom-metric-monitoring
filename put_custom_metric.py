# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import pprint
import random
import time
import requests

from google.cloud import monitoring_v3



def write_time_series(project_id, point_suffix, point_metric):
    # [START monitoring_write_timeseries]
    client = monitoring_v3.MetricServiceClient()
    project_name = client.project_path(project_id)

    series = monitoring_v3.types.TimeSeries()
    series.metric.type = 'custom.googleapis.com/' + point_suffix
    series.resource.type = 'gce_instance'
    series.resource.labels['instance_id'] = get_insatnce_id()
    series.resource.labels['zone'] = get_zone()
    point = series.points.add()
    point.value.double_value = point_metric
    now = time.time()
    point.interval.end_time.seconds = int(now)
    point.interval.end_time.nanos = int(
        (now - point.interval.end_time.seconds) * 10**9)
    pprint.pprint(series)
    client.create_time_series(project_name, [series])
    # [END monitoring_write_timeseries]

class MissingProjectIdError(Exception):
    pass


def get_insatnce_id():
    return requests.get("http://metadata.google.internal/computeMetadata/v1/instance/id",
         headers={'Metadata-Flavor': 'Google'}).text

def get_project_id():
    return requests.get("http://metadata.google.internal/computeMetadata/v1/project/project-id",
         headers={'Metadata-Flavor': 'Google'}).text

def get_zone():
    return requests.get("http://metadata.google.internal/computeMetadata/v1/instance/zone",
         headers={'Metadata-Flavor': 'Google'}).text.split('/')[-1]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Monitoring API operations.')

    parser.add_argument('metric_name', type=str, help='Metric name custom.googleapis.com/<metric_name>')
    parser.add_argument('metric_point', type=float, help='Metric point value (float)')

    args = parser.parse_args()

    write_time_series(get_project_id(), args.metric_name, args.metric_point)
