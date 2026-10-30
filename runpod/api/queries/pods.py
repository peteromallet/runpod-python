"""
Runpod | API Wrapper | Queries | GPUs
"""

import re


def generate_pod_mounts_query(pod_id):
    """Select only typed storage evidence for one exact pod, without secrets."""
    if not isinstance(pod_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", pod_id):
        raise ValueError("Invalid pod ID for mount observation")
    return f"""
    query podMounts {{
        pod(input: {{podId: "{pod_id}"}}) {{
            id
            volumeMounts {{
                volumeId
                volumeType
                mountPath
                readOnly
            }}
        }}
    }}
    """

QUERY_POD = """
query myPods {
    myself {
        pods {
            id
            containerDiskInGb
            costPerHr
            desiredStatus
            dockerArgs
            dockerId
            env
            gpuCount
            imageName
            lastStatusChange
            machineId
            memoryInGb
            name
            podType
            port
            ports
            uptimeSeconds
            vcpuCount
            volumeInGb
            volumeMountPath
            runtime {
                ports{
                    ip
                    isIpPublic
                    privatePort
                    publicPort
                    type
                }
            }
            machine {
                gpuDisplayName
                dataCenterId
            }
        }
    }
}
"""


def generate_pod_query(pod_id):
    """
    Generate a query for a specific GPU type
    """

    return f"""
    query pod {{
        pod(input: {{podId: "{pod_id}"}}) {{
            id
            containerDiskInGb
            costPerHr
            desiredStatus
            dockerArgs
            dockerId
            env
            gpuCount
            imageName
            lastStatusChange
            machineId
            memoryInGb
            name
            podType
            port
            ports
            uptimeSeconds
            vcpuCount
            volumeInGb
            volumeMountPath
            runtime {{
                ports {{
                    ip
                    isIpPublic
                    privatePort
                    publicPort
                    type
                }}
            }}
            machine {{
                gpuDisplayName
                dataCenterId
            }}
        }}
    }}
    """
