import base64
from io import BytesIO
from collections import defaultdict

from lib.facets.authorship import  createCatalogGroupForCanopy
from lib.open_exchange.utils import is_tildeid
from lib.predef.log import logger

from lib.open_exchange.open_fetch import (
    fetch_profile,
)
import numpy as np
from sklearn.metrics.cluster import adjusted_rand_score, normalized_mutual_info_score
import matplotlib.pyplot as plt

from s2and.eval import b3_precision_recall_fscore

from typing import List, Optional
from lib.predef.typedefs import AuthorID, AuthorQueryID
from lib.predef.utils import is_valid_email
from lib.shadowdb.data import MentionRecords

from lib.shadowdb.shadowdb import getShadowDB
import json

import math

def show_overview(canopy_count: int):
    print("show overview begin")
    db = getShadowDB()
    stats = {}

    # Fetch all canopies
    print("getting canopies")
    canopy_strs = db.get_canopy_strs()
    print("   .. done getting canopies")
    canopy_strs = canopy_strs[: canopy_count]
    canopies: List[MentionRecords] = []
    for cstr in canopy_strs:
        print(f"get {cstr}")
        c = db.get_canopy(cstr)
        canopies.append(c)

    # canopies = [db.get_canopy(cstr) for cstr in canopy_strs]
    stats["n_canopies"] = len(canopy_strs)

    # Signature counts by ID type
    n_email, n_tilde, n_noprofile = 0, 0, 0

    # For clustering metrics (ARI, NMI)
    gold_labels, pred_labels, baseline_pred_labels = [], [], []
    gold_lbl_to_idx, pred_lbl_to_idx = {}, {}

    # Aggregation variables
    paper_ids = set()
    unique_author_names = set()
    unique_authorid_w_profile = set()
    unique_authorid_w_email_noprofile = set()
    unique_authorid = set()
    sigs_w_profile = []
    sigs_wo_profile = []
    n_signatures = 0
    n_sigs_w_profile = 0
    n_sigs_by_canopy = []
    n_author_ids_by_canopy = []
    n_profiles_by_canopy = []
    unique_authorid_w_dblp = set()
    email_to_tilde_map = {}

    # Analyze canopies
    for canopy_idx, canopy in enumerate(canopies):
        if canopy_idx % 100 == 0:
            print(f"processing canopy {canopy_idx}")
        sigs = canopy.get_signatures()
        n_signatures += len(sigs)
        n_sigs_by_canopy.append(len(sigs))
        canopy_author_ids = set()
        canopy_profiles = set()
        for sig in sigs:
            gold_lbl = None
            paper_ids.add(sig.paper_id)
            if is_tildeid(sig.author_id):
                n_tilde += 1
                n_sigs_w_profile += 1
                gold_lbl = sig.author_id
                unique_authorid_w_profile.add(sig.author_id)
                unique_authorid.add(sig.author_id)
                canopy_profiles.add(sig.author_id)
                sigs_w_profile.append(sig)
            elif is_valid_email(sig.author_id):
                # For the current data (i.e. dblp records), this block will never be reached
                n_email += 1
                unique_authorid.add(sig.author_id)
                profile_id = None
                if sig.author_id in email_to_tilde_map:
                    profile_id = email_to_tilde_map[sig.author_id]
                else:
                    profile = fetch_profile(sig.author_id)
                    if profile is not None:
                        content = profile.content
                        username0 = content.names[0].username
                        profile_id = profile.id if is_tildeid(profile.id) else (
                            username0 if username0 and is_tildeid(username0) else None)
                if profile_id is not None:
                    email_to_tilde_map[sig.author_id] = profile_id
                    gold_lbl = profile_id
                    unique_authorid_w_profile.add(profile_id)
                    canopy_profiles.add(sig.author_id)
                    n_sigs_w_profile += 1
                    sigs_w_profile.append(sig)
                else:
                    unique_authorid_w_email_noprofile.add(sig.author_id)
                    sigs_wo_profile.append(sig)
            else:
                # If no OpenReview profile, OpenId for AuthorInfoBlock could be None or a DBLP string
                if sig.author_id.startswith("http"):  # DBLP url as id
                    unique_authorid_w_dblp.add(sig.author_id)
                # Do not include these for clustering evaluation
                # gold_lbl = f"no_profile_{n_noprofile}"
                n_noprofile += 1
                sigs_wo_profile.append(sig)
            if sig.author_id is not None:
                canopy_author_ids.add(sig.author_id)

            if gold_lbl is not None:
                if gold_lbl not in gold_lbl_to_idx:
                    gold_lbl_to_idx[gold_lbl] = len(gold_lbl_to_idx)
                gold_labels.append(gold_lbl_to_idx[gold_lbl])
                if sig.cluster_id not in pred_lbl_to_idx:
                    pred_lbl_to_idx[sig.cluster_id] = len(pred_lbl_to_idx)
                pred_labels.append(pred_lbl_to_idx[sig.cluster_id])
                baseline_pred_labels.append(canopy_idx)
            unique_author_names.add(sig.author_info.fullname)

        n_profiles_by_canopy.append(len(canopy_profiles))
        if len(canopy_profiles) == 0:
            print("No profile found")
        n_author_ids_by_canopy.append(len(canopy_author_ids))

    stats["n_signatures"] = n_signatures
    stats["n_papers"] = len(paper_ids)
    stats["n_authors"] = len(unique_authorid)
    stats["n_authors_w_profile"] = len(unique_authorid_w_profile)
    stats["n_authors_w_email_wo_profile"] = len(unique_authorid_w_email_noprofile)
    stats["n_unique_author_names"] = len(unique_author_names)
    stats["n_sigs_w_profile"] = n_sigs_w_profile
    stats["n_sigs_wo_profile"] = len(sigs_wo_profile)
    stats["n_sigs_w_email"] = n_email

    stats['n_sigs_by_canopy'] = n_sigs_by_canopy
    stats['min_sigs_by_canopy'] = min(n_sigs_by_canopy)
    stats['max_sigs_by_canopy'] = max(n_sigs_by_canopy)
    stats['mean_sigs_by_canopy'] = np.mean(n_sigs_by_canopy)
    stats['median_sigs_by_canopy'] = np.median(n_sigs_by_canopy)

    stats['n_profiles_by_canopy'] = n_profiles_by_canopy
    stats['min_profiles_by_canopy'] = min(n_profiles_by_canopy)
    stats['max_profiles_by_canopy'] = max(n_profiles_by_canopy)
    stats['mean_profiles_by_canopy'] = np.mean(n_profiles_by_canopy)
    stats['median_profiles_by_canopy'] = np.median(n_profiles_by_canopy)

    stats['n_author_ids_by_canopy'] = n_author_ids_by_canopy
    stats['min_author_ids_by_canopy'] = min(n_author_ids_by_canopy)
    stats['max_author_ids_by_canopy'] = max(n_author_ids_by_canopy)
    stats['mean_author_ids_by_canopy'] = np.mean(n_author_ids_by_canopy)
    stats['median_author_ids_by_canopy'] = np.median(n_author_ids_by_canopy)

    # Calculate clustering metrics
    stats["n_gold_clusters"] = len(set(gold_labels))
    stats["n_pred_clusters"] = len(set(pred_labels))
    gold_labels, pred_labels = np.array(gold_labels), np.array(pred_labels)
    ari = adjusted_rand_score(gold_labels, pred_labels)
    nmi = normalized_mutual_info_score(gold_labels, pred_labels)
    ari_nmi_avg = (ari + nmi) / 2
    stats["ari"], stats["nmi"], stats["ari_nmi_avg"] = ari, nmi, ari_nmi_avg
    # Calculate B3 F1
    gold_dict, pred_dict = defaultdict(list), defaultdict(list)
    for i in range(len(gold_labels)):
        gold_dict[gold_labels[i]].append(i)
        pred_dict[pred_labels[i]].append(i)
    precision, recall, f1, per_sig_metrics, _, _ = b3_precision_recall_fscore(gold_dict, pred_dict)
    stats["b3_precision"] = precision
    stats["b3_recall"] = recall
    stats["b3_f1"] = f1

    # Baseline, `bl` (with canopies instead of predicted clusters)
    bl_pred_labels = np.array(baseline_pred_labels)
    bl_ari = adjusted_rand_score(gold_labels, bl_pred_labels)
    bl_nmi = normalized_mutual_info_score(gold_labels, bl_pred_labels)
    bl_ari_nmi_avg = (bl_ari + bl_nmi) / 2
    stats["bl_ari"], stats["bl_nmi"], stats["bl_ari_nmi_avg"] = bl_ari, bl_nmi, bl_ari_nmi_avg
    # Calculate B3 F1
    bl_pred_dict = defaultdict(list)
    for i in range(len(gold_labels)):
        bl_pred_dict[bl_pred_labels[i]].append(i)
    bl_precision, bl_recall, bl_f1, bl_per_sig_metrics, _, _ = b3_precision_recall_fscore(gold_dict, bl_pred_dict)
    stats["bl_b3_precision"] = bl_precision
    stats["bl_b3_recall"] = bl_recall
    stats["bl_b3_f1"] = bl_f1


    # Evaluate gold and predicted cluster mismatch

    # Gold cluster over-splitting
    n_splits_per_gold_cluster, n_split_gold_clusters = [], 0
    for gold_cluster_indices in gold_dict.values():
        pred_splits = set([pred_labels[g] for g in gold_cluster_indices])
        n_splits_per_gold_cluster.append(len(pred_splits))
        n_split_gold_clusters += int(len(pred_splits) > 1)
    stats["n_splits_per_gold_cluster"] = n_splits_per_gold_cluster
    stats["min_splits_per_gold_cluster"] = min(n_splits_per_gold_cluster)
    stats["max_splits_per_gold_cluster"] = max(n_splits_per_gold_cluster)
    stats["mean_splits_per_gold_cluster"] = np.mean(n_splits_per_gold_cluster)
    stats["median_splits_per_gold_cluster"] = np.median(n_splits_per_gold_cluster)
    stats["n_split_gold_clusters"] = n_split_gold_clusters
    stats["n_split_gold_clusters_pct"] = f"{100.0 * n_split_gold_clusters / len(n_splits_per_gold_cluster)} %"

    # Gold cluster over-merging
    n_merged_per_pred_cluster, n_overmerged_pred_clusters = [], 0
    for pred_cluster_indices in pred_dict.values():
        gold_merges = set([gold_labels[p] for p in pred_cluster_indices])
        n_merged_per_pred_cluster.append(len(gold_merges))
        n_overmerged_pred_clusters += int(len(gold_merges) > 1)
    stats["n_merged_per_pred_cluster"] = n_merged_per_pred_cluster
    stats["min_merged_per_pred_cluster"] = min(n_merged_per_pred_cluster)
    stats["max_merged_per_pred_cluster"] = max(n_merged_per_pred_cluster)
    stats["mean_merged_per_pred_cluster"] = np.mean(n_merged_per_pred_cluster)
    stats["median_merged_per_pred_cluster"] = np.median(n_merged_per_pred_cluster)
    stats["n_overmerged_pred_clusters"] = n_overmerged_pred_clusters
    stats["n_overmerged_pred_clusters_pct"] = f"{100.0 * n_overmerged_pred_clusters / len(n_merged_per_pred_cluster)} %"


    # Evaluate no-profile subset of signatures
    n_predicted_links = 0.
    n_predicted_profiles_for_linking = []
    unlinked_cluster_labels = set()
    for sig in sigs_wo_profile:
        cluster_lbl = sig.cluster_id
        if cluster_lbl in pred_lbl_to_idx:
            # can be linked
            n_predicted_links += 1
            cluster_idx = pred_lbl_to_idx[cluster_lbl]
            cands = set()
            for i in pred_dict[cluster_idx]:
                if sigs_w_profile[i].author_id is not None:
                    cands.add(sigs_w_profile[i].author_id)
            n_predicted_profiles_for_linking.append(len(cands))
        else:
            unlinked_cluster_labels.add(cluster_lbl)
    stats["n_predicted_links"] = n_predicted_links
    stats["n_predicted_profiles_for_linking"] = n_predicted_profiles_for_linking
    stats["n_new_profiles_found"] = len(unlinked_cluster_labels)

    print(stats.keys())

    with open('stats.json', mode="w", encoding="utf-8") as f:
        json.dump(stats, f)

    # Generate plots

    # stats['plots'] = {}
    # # Generate the figure **without using pyplot**.
    # plt.hist(n_sigs_by_canopy)
    # # Save it to a temporary buffer.
    # buf = BytesIO()
    # plt.savefig(buf, format="png")
    # # Embed the result in the html output.
    # data = base64.b64encode(buf.getbuffer()).decode("ascii")
    # stats['plots']['test'] = data
    # <img src = "data:image/png;base64,{{stats['plots']['test']}}" />
