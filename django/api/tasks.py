from mantistable.celery import app
from api.models import Job
from api.process.utils import table
from api.process.utils.rules import person_rule as rules
from api.process.utils.mongo.repository import Repository

from api.process.normalization import normalizer, cleaner, cleaner_light
from api.process.column_analysis import column_classifier
from api.process.data_retrieval import cells as cells_data_retrieval
from api.process.data_retrieval import links as links_data_retrieval

from api.process.cea import cea
from api.process.cea.models.cell import Cell
from api.process.cpa import cpa
from api.process.revision import revision

from api.process.utils.assets import Assets

from celery import group
from multiprocessing import Manager

import mantistable.settings
import os
import mmap
import requests
import json
import math
import concurrent.futures

# TODO: EXtract constants
THREADS = 4
manager = Manager()
#candidates_index = manager.dict()

# TODO: Extract to utils
def generate_chunks(iterable, n):
    assert (n > 0)
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]


def job_slot(job_id: int):
    job = Job.objects.get(id=job_id)

    tables = [
        (table_id, table_name, table_data)
        for table_id, table_name, table_data in job.tables
    ]

    #data_preparation_phase(tables, job_id)
    workflow = data_preparation_phase.s(tables, job_id) | data_retrieval_phase.s(job_id) | computation_phase.s(job_id) | clean_up.si(job_id)
    return workflow.apply_async()

@app.task(name="data_preparation_phase", bind=True)
def data_preparation_phase(self, tables, job_id):
    self.replace(group([
        data_preparation_table_phase.s(job_id, *table)
        for table in tables
    ]))

@app.task(name="data_preparation_table_phase")
def data_preparation_table_phase(job_id, table_id, table_name, table_data):
    job = Job.objects.get(id=job_id)

    print(f"Normalization")
    normalization_result = _normalization_phase(table_id, table_data)
    client_callback(job, table_id, "normalization", normalization_result)
    
    print(f"Column Analysis")
    col_analysis_result = _column_analysis_phase(table_id, table_name, table_data, normalization_result)
    client_callback(job, table_id, "column analysis", col_analysis_result)

    return table_id, table_data, col_analysis_result

def _normalization_phase(table_id, data):
    table_model = table.Table(table_id=table_id, table=data)
    metadata = normalizer.Normalizer(table_model).normalize()
    return metadata

def _column_analysis_phase(table_id, table_name, table, data):
    stats = {
        col_name: d["stats"]
        for col_name, d in data.items()
    }

    cea_targets = Assets().get_json_asset("ne_cols.json")
    targets = cea_targets[table_name]
    
    if len(targets) > 0:
        cc = column_classifier.ColumnClassifierTargets(stats, targets)
    else:
        cc = column_classifier.ColumnClassifier(stats)
    
    tags = cc.get_columns_tags()
    
    metadata = {
        col_name: {**prev_meta, **tags[col_name]}
        for col_name, prev_meta in data.items()
    }

    return metadata

@app.task(name="data_retrieval_phase", bind=True)
def data_retrieval_phase(self, tables, job_id):
    job = Job.objects.get(id=job_id)
    job.progress["current"] = 1
    job.save()


    print(f"Data retrieval")

    cells_content = set()
    for table in tables:
        metadata = table[2]
        tags = [
            col_val["tags"]["col_type"]
            for col_val in metadata.values()
        ]

        for col_idx, col_val in enumerate(metadata.values()):
            for values in col_val["values"]:
                if tags[col_idx] != "LIT":
                    # Apply rules
                    # TODO:
                    """
                    rule = rules.PersonRule(values["original"])
                    if rule.match():
                        query = rule.build_query()
                    else:
                        query = values["normalized"]
                    """
                    query = values["normalized"]

                    cells_content.add(query)
    
    cells_content = list(cells_content)

    self.replace(
        data_retrieval_group_phase.si(job_id, cells_content) |
        dummy_phase.si(tables)
    )

    """
    CHUNK_SIZE = int(math.ceil(len(cells_content) / THREADS))
    chunks = generate_chunks(cells_content, CHUNK_SIZE)

    self.replace(
        group([
            data_retrieval_group_phase.si(job_id, chunk)
            for chunk in chunks
        ]) | data_retrieval_links_phase.si(job_id, tables)
    )
    """

@app.task(name="data_retrieval_group_phase")
def data_retrieval_group_phase(job_id, chunk):
    job = Job.objects.get(id=job_id)
    elastic_result = cells_data_retrieval.CandidatesRetrieval(chunk, job.backend).get_candidates()

    print("Clean lamapi results")
    data_retrieval_result = {}
    for cell in elastic_result.keys():
        """ TODO: Implement
        if len(elastic_result[cell]) == 0:
            client_callback(Job.objects.get(id=job_id), -1, "debug", f"No candidates for '{cell}'")
        """

        for res in elastic_result[cell]:
            label = res["label"]
            entity = res["uri"]

            norm_label = cleaner_light.CleanerLight(label).clean()
            if cell not in data_retrieval_result:
                data_retrieval_result[cell] = []
            
            data_retrieval_result[cell].append((norm_label, entity))

    candidates_index = {}
    with open(os.path.join(mantistable.settings.MEDIA_ROOT, "candidates.map"), "w") as f:
        last_offset = 0
        for cell in data_retrieval_result:
            content = json.dumps(data_retrieval_result[cell])
            content = content + "\n"
            f.write(content)
            candidates_index[cell] = (last_offset, len(content))
            last_offset += len(content)

    with open(os.path.join(mantistable.settings.MEDIA_ROOT, "candidates.index"), "w") as f_idx:
        json.dump(candidates_index, f_idx)
"""
@app.task(name="data_retrieval_links_phase", bind=True)
def data_retrieval_links_phase(self, job_id, tables):
    print(f"Data retrieval links")
    candidates = shared_memory

    def get_candidates(raw_cell, norm_cell):
        rule = rules.PersonRule(raw_cell)
        if rule.match():
            query = rule.build_query()
        else:
            query = norm_cell

        return candidates.get(query, [])

    pairs = {}
    for table in tables:
        metadata = table[2]
        tags = [
            col_val["tags"]["col_type"]
            for col_val in metadata.values()
        ]

        rows = []
        for row_idx in range(0, len(metadata[list(metadata.keys())[0]]["values"])):
            rows.append([])
            for col_idx in range(0, len(metadata.keys())):
                values = metadata[list(metadata.keys())[col_idx]]["values"][row_idx]
                rows[-1].append(values)

        for values in rows:
            subject_cell_raw = values[0]["original"]
            subject_norm = values[0]["normalized"]
            subject_candidates = get_candidates(subject_cell_raw, subject_norm)
            object_cells = values[1:]

            for idx, obj_cell in enumerate(object_cells):
                obj_raw = obj_cell["original"]
                
                if tags[idx + 1] != "LIT":
                    obj_norm = obj_cell["normalized"]
                else:
                    obj_norm = obj_raw

                obj_candidates = get_candidates(obj_raw, obj_norm)

                pair = (
                    (subject_cell_raw, subject_norm, subject_candidates, False),
                    (obj_raw, obj_norm, obj_candidates, tags[idx + 1] == "LIT"),
                )
                pairs[(subject_cell_raw, obj_raw)] = pair
    
    CHUNK_SIZE = 20
    chunks = generate_chunks(list(pairs.values()), CHUNK_SIZE)

    self.replace(
        group([
            data_retrieval_links_group_phase.si(job_id, chunk)
            for chunk in chunks
        ]) | dummy_phase.s(tables)
    )
"""

@app.task(name="data_retrieval_links_group_phase")
def data_retrieval_links_group_phase(job_id, chunk):
    job = Job.objects.get(id=job_id)
    links = links_data_retrieval.LinksRetrieval(chunk, job.backend).get_links()

    links = {
        hash(k): v
        for k,v in links.items()
    }

    return links

"""
@app.task(name="dummy_phase")
def dummy_phase(triples, tables):
    joined_triples = {}
    for triple in triples:
        joined_triples.update(triple)

    return tables, joined_triples
"""

@app.task(name="dummy_phase")
def dummy_phase(tables):
    return tables

@app.task(name="computation_phase", bind=True)
def computation_phase(self, info, job_id):
    tables = info
    job = Job.objects.get(id=job_id)
    job.progress["current"] = 2
    job.save()

    print("Computation")
    self.replace(
        group([
            computation_table_phase.s(job_id, *table)
            for table in tables
        ])
    )

@app.task(name="computation_table_phase")
def computation_table_phase(job_id, table_id, table_data, columns):
    job = Job.objects.get(id=job_id)



    print("Computation table")
    tags = [
        col_val["tags"]["col_type"]
        for col_val in columns.values()
    ]

    normalized = {
        values["original"]: values["normalized"]
        for col_val in columns.values()
        for values in col_val["values"]
    }

    candidates_index = {}
    with open(os.path.join(mantistable.settings.MEDIA_ROOT, "candidates.index"), "r") as f_idx:
        candidates_index = json.loads(f_idx.read())

    candidates = {}
    with open(os.path.join(mantistable.settings.MEDIA_ROOT, "candidates.map"), "r") as f:
        candidates_map = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        for norm in normalized.values():
            info = candidates_index.get(norm, None)
            if info is not None:
                offset = info[0]
                size = info[1]
                candidates_map.seek(offset)
                candidates[norm] = json.loads(candidates_map.read(size))

    print ("CEA")
    cea_results = cea.CEAProcess(
        table.Table(table_id=table_id, table=table_data),
        #triples=triples,
        tags=tags,
        normalized_map=normalized,
        candidates_map=candidates
    ).compute(job.backend)

    print(cea_results)

    print ("CPA")
    cpa_results = cpa.CPAProcess(
        cea_results
    ).compute()

    print(cpa_results)

    print ("Revision")
    revision_results = revision.RevisionProcess(
        cea_results, 
        cpa_results
    ).compute()
    client_callback(job, table_id, "computation", revision_results)

    #print(revision_results)

    #return table_id, table_data, revision_results


@app.task(name="clean_up")
def clean_up(job_id):
    job = Job.objects.get(id=job_id)
    job.progress["current"] = 3
    job.save()

    client_callback(job, -1, "end", {})

    # TODO: For now just delete job
    job.delete()

# ====================================================

def client_callback(job, table_id, header: str, payload=None):
    assert header is not None and len(header) > 0   # Contract

    if payload is None:
        payload = { }

    message = {
        "job_id": job.id,
        "table_id": table_id,
        "header": header,
        "payload": payload
    }

    try:
        response = requests.post(job.callback, json=message)
        print("sent to:", job.callback)
    except Exception as e:
        # Send to morgue?
        print("Error", e)
        return

    if response.status_code != 200:
        # Send to morgue?
        print("Response error", response.status_code)
        pass
