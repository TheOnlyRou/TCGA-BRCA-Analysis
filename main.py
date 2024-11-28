from bravado.client import SwaggerClient
import pandas as pd

cbioportal = SwaggerClient.from_url('https://www.cbioportal.org/api/v2/api-docs',
                                    config={"validate_requests":False,"validate_responses":False,"validate_swagger_spec": False})

for a in dir(cbioportal):
    cbioportal.__setattr__(a.replace(' ', '_').lower(), cbioportal.__getattr__(a))

muts = cbioportal.mutations.getMutationsInMolecularProfileBySampleListIdUsingGET(
    molecularProfileId="brca_tcga_mutations", # {study_id}_mutations gives default mutations profile for study
    sampleListId="brca_tcga_all", # {study_id}_all includes all samples
    projection="DETAILED" # include gene info
).result()

mutation_data = []
for mut in muts:
    mutation_data.append({
        "Gene": mut.gene.hugoGeneSymbol,
        "EntrezGeneId": mut.entrezGeneId,
        "MutationType": mut.mutationType,
        "ProteinChange": mut.proteinChange,
        "Chr": mut.chr,
        "StartPos": mut.startPosition,
        "EndPos": mut.endPosition,
        "VariantType": mut.variantType,
        "SampleId": mut.sampleId,
        "PatientId": mut.patientId,
        "TumorAltCount": mut.tumorAltCount,
        "TumorRefCount": mut.tumorRefCount
    })

# Convert to DataFrame
df = pd.DataFrame(mutation_data)
print(df.head())

# Fetch all sample IDs for the study
print(dir(cbioportal.samples))
samples = cbioportal.samples.getAllSamplesInStudyUsingGET(
    studyId="brca_tcga"
).result()

# Extract sample identifiers
sample_identifiers = [{"sampleId": sample.sampleId} for sample in samples]
print(f"Number of sample identifiers fetched: {len(sample_identifiers)}")

# Print all operations for the resource
print(dir(cbioportal.copy_number_segments))

# print(cbioportal.copy_number_segments.fetchCopyNumberSegmentsUsingPOST.__doc__)

cnv_data = cbioportal.copy_number_segments.fetchCopyNumberSegmentsUsingPOST(
    sampleIdentifiers=sample_identifiers,  # Provide sample IDs
).result()
print(f"Number of Copy Number Segments: {len(cnv_data)}")
# Parse and merge with existing DataFrame
print(cnv_data)
# cnv_df = pd.DataFrame([
#     {"SampleId": item.sampleId, "Gene": item.gene.hugoGeneSymbol, "Log2CopyRatio": item.value}
#     for item in cnv_data
# ])
# df = df.merge(cnv_df, on=["SampleId", "Gene"], how="left")

df.to_csv("tcga_brca_mutations.csv", index=False)
