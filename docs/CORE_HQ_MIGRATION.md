# CORE HQ external resource migration — pending founder approval

Current visible name: CORE HQ (CORE Headquarters). Historical records retain CORE GENESIS. No external resource was renamed, pushed or deployed.

| Resource | Current value | Reviewable migration procedure |
| --- | --- | --- |
| Local HQ folder | `~/core-genesis` | After stopping local servers, verify clean/stashed work, rename only with approval, update local tooling paths and validate startup. Roll back by restoring the folder name. Python package stays `core_genesis` for compatibility. |
| GitHub | `vincentleg/core-genesis` | With approval, rename repository to an available `core-hq`, verify GitHub redirects, update origin and current links/CI settings; preserve historical source links and tags. Verify clone and issues before updating public references. Rollback requires checking repository-name availability and redirects. |
| Vercel project | Existing CORE GENESIS project | Inspect actual project identity, free-plan settings, Git integration and deployment history first. Rename only after approval; keep the old demo alias and historical build accessible. Do not create a paid plan or assume a project-name change preserves every alias. |
| HQ domain | `core-genesis-living.vercel.app` | Select an available free alias with founder approval. Keep the old hackathon demo reachable and clearly label its historical version. Preview the HQ build, verify evidence links and metadata, then request explicit deployment approval. No automatic DNS changes or domain purchase. |
| CORE public website | `creationofrebornearth.com` | Outside HQ rename scope. Founder reports older CORE in production; local V9.2 is undeployed. Do not rename, deploy or equate it with local V9.2. |

Before any approved external migration: capture current configuration and rollback commands, inspect the exact diff/build, verify links, preserve hackathon evidence and confirm no cost change. Permission to rename is not permission to deploy CORE or send source to an external model.
