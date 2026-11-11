# Incremental KG Fusion Demonstration (Synthetic Example)

This document is a synthetic knowledge-fusion test. Its new entities and relations are fictional and must not be imported into a production knowledge graph.

## Existing registered tool: NameToSMILES

Name: NameToSMILES
Category: Chemical Tool
Function: Query the corresponding SMILES format based on the molecule name
Input: molecule name
Output: SMILES
Safety: Yes
Source: PubChem PUG REST API

The previously registered tool NameToSMILES uses FusionMarker_Z91 in this synthetic demonstration. This relation is test-only, not an assertion about the real implementation.

## New documentation-only scientific tool: KGFusionTestTool

Name: KGFusionTestTool
Category: Chemical Tool
Function: Produce a synthetic test marker from SMILES
Input: SMILES
Output: FusionMarker_Z91
Safety: Yes
Source: Test Document

KGFusionTestTool is a documentation-only tool with no registered Python implementation. It cannot be executed by ToolsAgent.

## Additional new knowledge

FusionMarker_Z91 is associated with FusionResult_Q74. Both identifiers are invented for this test.
