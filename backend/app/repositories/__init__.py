"""Repositories package — the data-access layer.

Repositories are the ONLY place that issues database queries. Services depend on
repositories (not on the ORM directly), which keeps persistence details
isolated and gives multi-user scoping a single enforcement point: when auth
lands, ``user_id`` filtering is added here once rather than in every service.

No logic is implemented in this step.
"""
