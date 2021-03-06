import requests
import json
import os
from api.process.utils.decorators import retry_on_exception


class LamAPIWrapper:
    def __init__(self, endpoint: str, port: int, access_token: str, timeout=120):
        self._endpoint = endpoint
        self._port = port
        self._access_token = access_token
        self._timeout = timeout

    def infos(self):
        return self._make_request(
            lambda: requests.get(
                self._api_url("infos"),
                timeout=2
            )
        )
            
    @retry_on_exception(max_retries=5, default=None)
    async def labels(self, label: str, session):
        def _elastic_url(suburl):
            if os.environ.get("LAMAPI", False):
                return f"http://mantistable4_api_elastic:9200/{suburl}"
            else:
                return f"http://35.236.42.69:9200/{suburl}"


        if len(label) == 0:
            return []

        self._log("labels", f"{label}")

        """
        params = {
            "norm": label,
            "original": label, # Unused
            "token": self._access_token
        }
        """
        params = {
            "q": f'label:"{label}"',
            "size": 10000
        }

        async with session.get(
            _elastic_url("mantis/_search"),
            params=params,
            timeout=self._timeout
        ) as response:
            return await response.json()

    @retry_on_exception(max_retries=5, default=None)
    async def labels_fuzzy(self, label: str, session):
        def _elastic_url(suburl):
            if os.environ.get("LAMAPI", False):
                return f"http://mantistable4_api_elastic:9200/{suburl}"
            else:
                return f"http://35.236.42.69:9200/{suburl}"

        if len(label) == 0:
            return []

        self._log("labels", f"{label}")

        async with session.get(
            _elastic_url("mantis/_search"),
            params={
                "size": 10000,
                "filter_path": "took,hits.hits._source"
            },
            json={
                "query": {
                    "match": {
                        "label": {
                            "query": label,
                            "fuzziness": "AUTO",
                            "zero_terms_query": "all"
                        }
                    }
                }
            },
            timeout=self._timeout
        ) as response:
            print(response.status)
            return await response.json()

    @retry_on_exception(max_retries=5, default={})
    def predicates(self, data):
        if len(data) == 0:
            return {}

        self._log("predicates", data)
        return self._make_request(
            lambda: requests.post(
                self._api_url("predicates"),
                json={"json": data},
                params={"token": self._access_token},
                timeout=self._timeout
            )
        )

    @retry_on_exception(max_retries=5, default={})
    def objects(self, subjects):
        if len(subjects) == 0:
            return {}

        self._log("objects", subjects)
        return self._make_request(
            lambda: requests.post(
                self._api_url("objects"),
                json={"json": subjects},
                params={"token": self._access_token},
                timeout=self._timeout
            )
        )

    @retry_on_exception(max_retries=5, default={})
    def literals(self, subjects):
        if len(subjects) == 0:
            return {}

        self._log("literals", subjects)
        return self._make_request(
            lambda: requests.post(
                self._api_url("literals"),
                json={"json": subjects},
                params={"token": self._access_token},
                timeout=self._timeout
            )
        )

    @retry_on_exception(max_retries=5, default={})
    def concepts(self, entities):
        if len(entities) == 0:
            return {}

        self._log("concepts", entities)
        return self._make_request(
            lambda: requests.post(
                self._api_url("concepts"),
                json={"json": entities},
                params={"token": self._access_token},
                timeout=self._timeout
            )
        )

    def _api_url(self, suburl):
        return f"http://{self._endpoint}:{self._port}/{suburl}"

    def _make_request(self, requester):
        response = requester()
        if response.status_code != 200:
            return {}

        return response.json()

    def _log(self, endpoint_name, query):
        query = str(query).replace('\n', '')
        if len(query) > 20:
            query = query[0:20] + '...'
        print(f"LAMAPI {endpoint_name} {query}")


    # Deprecated for now
    """
    def _labels_impl(self, norm, original, results=None, cursor=None):
        if results is None:
            results = []

        params = {
            "norm": norm,
            "original": original,
            "token": self._access_token
        }

        if cursor is not None:
            params.update({
                "nextCursor": cursor
            })
        
        response = self._make_request(
            lambda: requests.get(
                self._api_url("labels"),
                params=params, 
                timeout=self._timeout
            )
        )

        if "results" in response:
            results.extend(response["results"])

            if "cursor" in response and response["count"] > 0:
                cursor = response["cursor"]
                results = self._labels_impl(norm, original, results, cursor)
            
            return results
        
        return response
    """


"""
if __name__ == "__main__":
    lapiw = LamAPIWrapper("149.132.176.50", 8097)
    res = lapiw.labels("batman")
    print(json.dumps(res, indent=4))
    print(len(res))

"""
