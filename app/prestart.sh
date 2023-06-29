#! /usr/bin/env bash
alembic revision --autogenerate -m "generate_schema"
alembic upgrade head
