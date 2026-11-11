import json
from pathlib import Path
import shutil
import tempfile
import unittest

from kg_management.manager import plan_deletion, commit_deletion, incident_edges


def create_kg(root: Path):
    g={'graph_dict':{
        'ToolA': [['is a','Chemical Tool'],['has the functionality that','Calculate X'],['inputs','SMILES'], ['uses','Marker']],
        'SMILES': [['is the input of','ToolA']],
        'Marker':[['associated with','Answer']],
        'ToolB':[['uses','Marker']],
    }}
    embedding={str(('ToolA','has the functionality that','Calculate X')):[1.0,2.0]}
    struct={'index_id':'id','summary':None,'table':{},'rel_map':{},'embedding_dict':embedding}
    idx={'index_store/data':{'id':{'__type__':'kg','__data__':json.dumps(struct)}}}
    for name,obj in [('graph_store.json',g),('index_store.json',idx)]:
        (root/name).write_text(json.dumps(obj),encoding='utf-8')
    for name in ['default__vector_store.json','image__vector_store.json']:
        (root/name).write_text(json.dumps({'embedding_dict':{}}),encoding='utf-8')
    (root/'docstore.json').write_text('{}',encoding='utf8')


class GraphManagementTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.kg=Path(self.temp.name)/'KG'
        self.kg.mkdir()
        create_kg(self.kg)
    def tearDown(self): self.temp.cleanup()

    def test_delete_single_relation_retains_other_edges(self):
        plan=plan_deletion(self.kg,triple=('ToolA','uses','Marker'))
        self.assertEqual(len(plan['triples_to_remove']),1)
        result=commit_deletion(self.kg,plan)
        self.assertEqual(result['removed_triples'],1)
        self.assertEqual(result['removed_embeddings'],0)
        self.assertEqual(result['remaining_triples'],6)
        g=json.loads((self.kg/'graph_store.json').read_text())['graph_dict']
        self.assertNotIn(['uses','Marker'],g['ToolA'])
        self.assertIn(['has the functionality that','Calculate X'],g['ToolA'])
        self.assertIn(['uses','Marker'],g['ToolB'])
        self.assertTrue(Path(result['backup']).is_dir())
        self.assertFalse((self.kg/'.scitoolagent_kg.lock').exists())

    def test_delete_entity_incoming_outgoing_and_embedding(self):
        edges=incident_edges(json.loads((self.kg/'graph_store.json').read_text())['graph_dict'],'ToolA')
        self.assertEqual(len(edges),5)
        plan=plan_deletion(self.kg,entity='ToolA')
        self.assertEqual(len(plan['triples_to_remove']),5)
        self.assertEqual(len(plan['embeddings_to_remove']),1)
        result=commit_deletion(self.kg,plan)
        self.assertEqual(result['removed_embeddings'],1)
        self.assertEqual(result['remaining_embeddings'],0)
        g=json.loads((self.kg/'graph_store.json').read_text())['graph_dict']
        self.assertNotIn('ToolA',g)
        self.assertNotIn('SMILES',g)
        self.assertIn('ToolB',g)

    def test_mirror_inverse_removed(self):
        p=plan_deletion(self.kg,triple=('ToolA','inputs','SMILES'))
        self.assertEqual(len(p['triples_to_remove']),2)
        r=commit_deletion(self.kg,p)
        self.assertEqual(r['removed_triples'],2)
        g=json.loads((self.kg/'graph_store.json').read_text())['graph_dict']
        self.assertNotIn('SMILES',g)

    def test_can_keep_mirror_when_explicitly_requested(self):
        p=plan_deletion(self.kg,triple=('ToolA','inputs','SMILES'),include_inverse=False)
        self.assertEqual(len(p['triples_to_remove']),1)

    def test_stale_preview_is_rejected(self):
        p=plan_deletion(self.kg,entity='ToolA')
        graph_file=self.kg/'graph_store.json'
        obj=json.loads(graph_file.read_text())
        obj['graph_dict']['ToolB'].append(['new','Fact'])
        graph_file.write_text(json.dumps(obj))
        with self.assertRaisesRegex(RuntimeError,'预览后已改变'):
            commit_deletion(self.kg,p)
        self.assertFalse((self.kg/'.scitoolagent_kg.lock').exists())

    def test_unsupported_index_is_rejected(self):
        index_file=self.kg/'index_store.json'
        idx=json.loads(index_file.read_text())
        struct=json.loads(idx['index_store/data']['id']['__data__'])
        struct['table']={'x':['some_doc']}
        idx['index_store/data']['id']['__data__']=json.dumps(struct)
        index_file.write_text(json.dumps(idx))
        with self.assertRaisesRegex(ValueError,'额外文档'):
            plan_deletion(self.kg,entity='ToolA')

if __name__=='__main__': unittest.main()
