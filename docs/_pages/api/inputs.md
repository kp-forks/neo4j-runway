---
permalink: /api/inputs/
title: UserInput
toc: true
toc_label: UserInput
toc_icon: "fa-solid fa-plane"
---

    from neo4j_runway import UserInput




## Class Methods


### __init__
A container for user provided information about the
        data.

    Attributes
    ----------
    general_description : str, optional
        A general description of the CSV data, by default =
        ""
    column_descriptions : Dict[str, str]
        A mapping of the desired CSV columns to their
        descriptions.
        The keys of this argument will determine which CSV
        columns are
        evaluated in discovery and used to generate a data
        model.
