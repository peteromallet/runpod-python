"""Offline exact-pod storage projection; no account listing or secrets selected."""

import json
from unittest.mock import patch

import pytest

import runpod
from runpod.api.queries.pods import generate_pod_mounts_query


def test_minimal_query_and_sdk_response_are_exact_and_fresh():
    response = {"id": "pod-1", "volumeMounts": [
        {"volumeId": "vol-1", "volumeType": "NETWORK_VOLUME", "mountPath": "/workspace", "readOnly": False}
    ]}
    with patch("runpod.api.graphql.requests.post") as post:
        post.return_value.json.return_value = {"data": {"pod": response}}
        assert runpod.get_pod_mounts("pod-1", api_key="offline-test") == response
        assert runpod.get_pod_mounts("pod-1", api_key="offline-test") == response
        assert post.call_count == 2
        query = json.loads(post.call_args.kwargs["data"])["query"]
    assert query == generate_pod_mounts_query("pod-1")
    assert 'pod(input: {podId: "pod-1"})' in query
    assert query.split("{", 2)[2].count("volumeMounts") == 1
    for field in ("volumeId", "volumeType", "mountPath", "readOnly"):
        assert field in query
    for excluded in ("myself", "env", "networkVolumeId", "objectStores", "runtime", "name", "volumeMountPath"):
        assert excluded not in query


@pytest.mark.parametrize("pod", [None, [], {}, {"id": "other"}, [{"id": "pod-1"}]])
def test_sdk_refuses_unjoinable_exact_pod(pod):
    with patch("runpod.api.graphql.requests.post") as post:
        post.return_value.json.return_value = {"data": {"pod": pod}}
        with pytest.raises(ValueError, match="Exact-pod"):
            runpod.get_pod_mounts("pod-1", api_key="offline-test")


@pytest.mark.parametrize("pod_id", [None, "", " pod-1", "p\n", 'p"}) { myself { id } } #', ["pod-1"], "x" * 129])
def test_invalid_pod_id_refuses_before_transport(pod_id):
    with patch("runpod.api.graphql.requests.post") as post:
        with pytest.raises(ValueError, match="Invalid pod ID"):
            runpod.get_pod_mounts(pod_id, api_key="offline-test")
        post.assert_not_called()


def test_partial_graphql_errors_never_establish_observation():
    with patch("runpod.api.graphql.requests.post") as post:
        post.return_value.json.return_value = {
            "data": {"pod": {"id": "pod-1", "volumeMounts": []}},
            "errors": [{"message": "typed projection unsupported"}],
        }
        with pytest.raises(runpod.error.QueryError):
            runpod.get_pod_mounts("pod-1", api_key="offline-test")


def test_partial_errors_rejected_even_with_custom_graphql_transport():
    with patch("runpod.api.ctl_commands.run_graphql_query", return_value={
        "data": {"pod": {"id": "pod-1", "volumeMounts": []}}, "errors": [{"message": "unsupported"}]
    }):
        with pytest.raises(ValueError, match="Exact-pod"):
            runpod.get_pod_mounts("pod-1", api_key="offline-test")
