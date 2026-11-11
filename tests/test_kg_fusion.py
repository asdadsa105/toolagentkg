"""Run: python -m unittest discover -s tests -p test_kg_fusion.py -v"""
import json
import tempfile
import unittest
from pathlib import Path

from kg_fusion.merge_planner import make_fusion_plan
from text_ingestion.excel_exporter import export_excel


class FusionPlannerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.kg = self.root / 'KG'
        self.kg.mkdir()
        self.old_function = 'Query the corresponding SMILES format based on the molecule name'
        original = {'graph_dict': {
            'NameToSMILES': [
                ['is a', 'Chemical Tool'],
                ['has the functionality that', self.old_function],
                ['inputs', 'molecule name'],
                ['outputs', 'SMILES'],
                ['is sourced from', 'Web API'],
                ['does not need', 'Security Check'],
            ]
        }}
        (self.kg / 'graph_store.json').write_text(json.dumps(original),encoding='utf-8')
        self.file = self.root / 'review.xlsx'

    def workbook(self, tools, triples=(), grounded=True):
        evidence=[]
        for tool in tools:
            evidence.append({
                'RecordType':'Tool','Subject':tool['Name'], 'Predicate':'tool_metadata',
                'Object':tool['Function'], 'Disposition':'Approved' if grounded else 'Rejected',
                'ChunkID':'chunk_1','Quote':'source citation'
            })
        for triple in triples:
            evidence.append({
                'RecordType':'Triple','Subject':triple['Subject'],
                'Predicate':triple['Predicate'],'Object':triple['Object'],
                'Disposition':'Approved' if grounded else 'Rejected',
                'ChunkID':'chunk_1','Quote':'source citation'
            })
        export_excel({'Tools':tools,'Triples':list(triples),'Evidence':evidence,'Review':[]},self.file,overwrite=True)

    def old_row(self, source='Web API', function=None):
        return dict(Category='Chemical Tool',Name='NameToSMILES',Function=function or self.old_function,
                    Input='molecule name',Output='SMILES',Safety='Yes',Source=source)

    def new_row(self):
        return dict(Category='Chemical Tool',Name='KGFusionTestTool',Function='Process an input token',
                    Input='molecule name',Output='string token',Safety='Yes',Source='Test Reference')

    def test_old_entity_source_is_opt_in(self):
        self.workbook([self.old_row(source='PubChem PUG REST')])
        plan = make_fusion_plan(self.file,self.kg)
        self.assertEqual(plan['stats']['existing_tools'],1)
        self.assertEqual(plan['stats']['source_candidates'],1)
        self.assertEqual(plan['tables']['Triples'],[])
        opt=plan['source_options'][0]['id']
        plan2=make_fusion_plan(self.file,self.kg,[opt])
        self.assertEqual(plan2['tables']['Triples'],[dict(Subject='NameToSMILES',Predicate='is sourced from',Object='PubChem PUG REST')])
        self.assertEqual(plan2['tables']['Tools'],[])

    def test_existing_contract_change_goes_to_review(self):
        self.workbook([self.old_row(function='Altered function from new doc')])
        plan=make_fusion_plan(self.file,self.kg)
        self.assertEqual(plan['stats']['new_tools'],0)
        self.assertEqual(plan['stats']['new_extra_triples'],0)
        self.assertTrue(any('Function' in r['Reason'] for r in plan['reviews']))

    def test_new_tool_and_grounded_general_relation(self):
        extra=[{'Subject':'NameToSMILES','Predicate':'uses','Object':'NewPubChemService'}]
        self.workbook([self.old_row(),self.new_row()],extra)
        plan=make_fusion_plan(self.file,self.kg)
        self.assertEqual(plan['stats']['new_tools'],1)
        self.assertEqual(plan['stats']['new_extra_triples'],1)
        self.assertEqual(plan['tables']['Triples'][0]['Predicate'],'uses')
        self.assertEqual(len(plan['tables']['Tools']),1)

    def test_unverified_relation_is_blocked(self):
        extra=[{'Subject':'NameToSMILES','Predicate':'uses','Object':'NewPubChemService'}]
        self.workbook([],extra,grounded=False)
        plan=make_fusion_plan(self.file,self.kg)
        self.assertEqual(plan['tables']['Triples'],[])
        self.assertTrue(any('Approved' in r['Reason'] for r in plan['reviews']))

    def test_manual_override_of_tool_contract_is_blocked(self):
        extra=[{'Subject':'NameToSMILES','Predicate':'outputs','Object':'new datatype'}]
        self.workbook([],extra)
        plan=make_fusion_plan(self.file,self.kg)
        self.assertEqual(plan['tables']['Triples'],[])
        self.assertTrue(any('工具契约' in r['Reason'] for r in plan['reviews']))


if __name__=='__main__':
    unittest.main()
