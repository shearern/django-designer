Django Design Tools
===================


Example Design File
-------------------

    ---
    name:   sbc_sermons
    title:  SBC Sermon Catalog
    models:
      Recording:
        fields:
          - title
          - recording_id
          - recorded_at
          - speakers
          - series
          - session
          - sbc_class
          - hidden
          - v2_website_nid
        features:
          - Auto-calculate recording ID?
      Speaker:
        fields:
          - title
          - first_name
          - last_name
          - v2_title
      SbcClass:
        fields:
          - title
          - record_id_ind
      Series:
        fields:
          - title
          - v2_nid
          - summary
      CoverImage:
        fields:
          - image
    pages:
      Index:
        features:
          - See what recording tasks are needed
          - Show table of recordings
      ClassIndex:
        parent: Index
        features:
          - Show table of all classes defined

    features:
      - Create new recording stubs on a schedule

