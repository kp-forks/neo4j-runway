import unittest

from neo4j_runway.code_generation.cypher import (
    cast_value,
    generate_constraints_key,
    generate_match_node_clause,
    generate_match_same_node_labels_clause,
    generate_merge_node_clause_standard,
    generate_merge_node_load_csv_clause,
    generate_merge_relationship_clause_standard,
    generate_merge_relationship_load_csv_clause,
    generate_node_key_constraint,
    generate_relationship_key_constraint,
    generate_set_property,
    generate_set_unique_property,
    generate_unique_constraint,
)
from neo4j_runway.models import DataModel, Node, Property, Relationship
from tests.resources.answers.ingestion_generation_answers import (
    constraint_a_1,
    constraint_a_3,
    constraint_b,
    constraints_key_a_1,
    constraints_key_a_3,
    constraints_key_b,
    match_node_a,
    match_node_b,
    match_same_labels,
    merge_node_load_csv_b,
    merge_node_standard_a,
    merge_relationship_load_csv,
    merge_relationship_standard,
    merge_relationship_standard_different_files,
    merge_relationship_standard_same_node,
    node_key_constraint_answer,
    relationship_key_constraint_answer,
    set_properties_a,
    set_properties_b,
    set_unique_property_a,
    set_unique_property_b,
)


class TestIngestCodeGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        prop_a_1 = Property(
            name="uniqueProp1",
            column_mapping="unique_prop_1",
            type="str",
            is_unique=True,
        )
        prop_a_2 = Property(
            name="prop1", column_mapping="prop_1", type="str", is_unique=False
        )
        prop_a_3 = Property(
            name="uniqueProp3",
            column_mapping="unique_prop_3",
            type="str",
            is_unique=True,
        )
        prop_b_1 = Property(
            name="uniqueProp2",
            column_mapping="unique_prop_2",
            type="str",
            is_unique=True,
        )
        prop_b_2 = Property(
            name="prop2", column_mapping="prop_2", type="str", is_unique=False
        )
        prop_b_3 = Property(
            name="prop3", column_mapping="prop_3", type="str", is_unique=False
        )
        prop_rel_1 = Property(
            name="relProp", column_mapping="rel_prop", type="int", is_unique=False
        )

        cls.node_a = Node(label="NodeA", properties=[prop_a_1, prop_a_2, prop_a_3])
        cls.node_b = Node(label="NodeB", properties=[prop_b_1, prop_b_2, prop_b_3])
        cls.rel_1 = Relationship(
            type="HAS_RELATIONSHIP",
            properties=[prop_rel_1],
            source=cls.node_a.label,
            target=cls.node_b.label,
        )

        cls.data_model = DataModel(
            nodes=[cls.node_a, cls.node_b], relationships=[cls.rel_1]
        )

    def test_generate_constraints_key(self) -> None:
        """
        Generate the key for a unique constraint.
        """

        label = self.node_a.label
        unique_props = self.node_a.unique_properties
        print(unique_props[0].name)
        self.assertEqual(
            generate_constraints_key(
                label_or_type=label, unique_property=unique_props[0]
            ),
            constraints_key_a_1,
        )
        self.assertEqual(
            generate_constraints_key(
                label_or_type=label, unique_property=unique_props[1]
            ),
            constraints_key_a_3,
        )

        label = self.node_b.label
        unique_props = self.node_b.unique_properties
        self.assertEqual(
            generate_constraints_key(
                label_or_type=label, unique_property=unique_props[0]
            ),
            constraints_key_b,
        )

    def test_generate_constraint(self) -> None:
        """
        Generate a constraint string.
        """

        label = self.node_a.label
        unique_props = self.node_a.unique_properties
        self.assertEqual(
            generate_unique_constraint(
                label_or_type=label, unique_property=unique_props[0]
            ),
            constraint_a_1,
        )
        self.assertEqual(
            generate_unique_constraint(
                label_or_type=label, unique_property=unique_props[1]
            ),
            constraint_a_3,
        )

        label = self.node_b.label
        unique_props = self.node_b.unique_properties
        self.assertEqual(
            generate_unique_constraint(
                label_or_type=label, unique_property=unique_props[0]
            ),
            constraint_b,
        )

    def test_generate_match_node_clause(self) -> None:
        """
        Generate a MATCH node clause.
        """

        self.assertEqual(
            generate_match_node_clause(node=self.node_a),
            match_node_a,
        )

        self.assertEqual(
            generate_match_node_clause(node=self.node_b),
            match_node_b,
        )

    def test_generate_set_property(self) -> None:
        """
        Generate a set property string.
        """

        unique_map = self.node_a.unique_properties_column_mapping
        prop_map = self.node_a.property_column_mapping
        for k in unique_map.keys():
            del prop_map[k]
        self.assertEqual(
            generate_set_property(
                properties=self.node_a.nonunique_properties, strict_typing=False
            ),
            set_properties_a,
        )

        unique_map = self.node_b.unique_properties_column_mapping
        prop_map = self.node_b.property_column_mapping
        for k in unique_map.keys():
            del prop_map[k]
        self.assertEqual(
            generate_set_property(
                properties=self.node_b.nonunique_properties, strict_typing=False
            ),
            set_properties_b,
        )

    def test_generate_set_unique_property(self) -> None:
        """
        Generate the unique properties to match a node on within a MERGE statement.
        """

        self.assertEqual(
            generate_set_unique_property(
                unique_properties=self.node_a.unique_properties, strict_typing=False
            ),
            set_unique_property_a,
        )
        self.assertEqual(
            generate_set_unique_property(
                unique_properties=self.node_b.unique_properties, strict_typing=False
            ),
            set_unique_property_b,
        )

    def test_generate_merge_node_clause_standard(self) -> None:
        """
        Generate a MERGE node clause.
        """

        self.assertEqual(
            generate_merge_node_clause_standard(node=self.node_a, strict_typing=False),
            merge_node_standard_a,
        )

    def test_generate_merge_node_load_csv_clause(self) -> None:
        """
        Generate a MERGE node clause for the LOAD CSV method.
        """

        self.assertEqual(
            generate_merge_node_load_csv_clause(
                node=self.node_b,
                source_name="test.csv",
                method="api",
                strict_typing=False,
            ),
            merge_node_load_csv_b,
        )

    def test_generate_merge_relationship_clause_standard(self) -> None:
        """
        Generate a MERGE relationship clause.
        """

        self.assertEqual(
            generate_merge_relationship_clause_standard(
                relationship=self.rel_1,
                source_node=self.node_a,
                target_node=self.node_b,
                strict_typing=True,
            ),
            merge_relationship_standard,
        )

    def test_generate_merge_relationship_load_csv_clause(self) -> None:
        """
        Generate a MERGE relationship clause for the LOAD CSV method.
        """

        self.assertEqual(
            generate_merge_relationship_load_csv_clause(
                relationship=self.rel_1,
                source_node=self.node_a,
                target_node=self.node_b,
                source_name="test.csv",
                method="browser",
                batch_size=50,
                strict_typing=True,
            ),
            merge_relationship_load_csv,
        )

    def test_generate_match_same_labels_different_csv_mapping(self) -> None:
        node = Node(
            label="Person",
            properties=[
                Property(
                    name="name",
                    type="str",
                    column_mapping="name",
                    alias="knows_person",
                    is_unique=True,
                )
            ],
        )
        self.assertEqual(
            generate_match_same_node_labels_clause(node=node), match_same_labels
        )

    def test_generate_merge_relationship_clause_standard_with_same_node(self) -> None:
        node = Node(
            label="Person",
            properties=[
                Property(
                    name="name",
                    type="str",
                    column_mapping="name",
                    alias="knows_person",
                    is_unique=True,
                )
            ],
        )
        rel = Relationship(
            type="KNOWS", source="Person", target="Person", properties=[]
        )

        self.assertEqual(
            generate_merge_relationship_clause_standard(
                relationship=rel,
                source_node=node,
                target_node=node,
                strict_typing=False,
            ),
            merge_relationship_standard_same_node,
        )

    def test_generate_relationship_with_nodes_different_source_files(self) -> None:
        node_a = Node(
            label="Person",
            properties=[
                Property(
                    name="name",
                    type="str",
                    column_mapping="name",
                    alias="person_name",
                    is_unique=True,
                )
            ],
            source_name="owners.csv",
        )
        node_b = Node(
            label="Pet",
            properties=[
                Property(
                    name="name",
                    type="str",
                    column_mapping="name",
                    is_unique=True,
                )
            ],
            source_name="pets.csv",
        )
        rel = Relationship(
            type="LOVES",
            source="Pet",
            target="Person",
            properties=[],
            source_name="pets.csv",
        )

        self.assertEqual(
            generate_merge_relationship_clause_standard(
                relationship=rel,
                source_node=node_b,
                target_node=node_a,
                strict_typing=True,
            ),
            merge_relationship_standard_different_files,
        )

    def test_generate_node_key_constraint(self) -> None:
        nk1 = Property(name="nk1", type="str", column_mapping="nk1", part_of_key=True)
        nk2 = Property(name="nk2", type="str", column_mapping="nk2", part_of_key=True)

        self.assertEqual(
            generate_node_key_constraint(label="NodeA", unique_properties=[nk1, nk2]),
            node_key_constraint_answer,
        )

    def test_generate_relationship_key_constraint(self) -> None:
        nk1 = Property(name="nk1", type="str", column_mapping="nk1", part_of_key=True)
        nk2 = Property(name="nk2", type="str", column_mapping="nk2", part_of_key=True)

        self.assertEqual(
            generate_relationship_key_constraint(
                type="HAS_RELATIONSHIP", unique_properties=[nk1, nk2]
            ),
            relationship_key_constraint_answer,
        )

    def test_cast_no_type(self) -> None:
        prop_str = Property(name="p1", type="str", column_mapping="p1")
        self.assertEqual(cast_value(prop_str), "row.p1")

    def test_cast_date(self) -> None:
        prop_date = Property(name="p3", type="Date", column_mapping="p3")
        self.assertEqual(cast_value(prop_date), "date(row.p3)")

    def test_cast_time(self) -> None:
        prop_time = Property(name="p4", type="Time", column_mapping="p4")
        self.assertEqual(cast_value(prop_time), "time(row.p4)")

    def test_cast_datetime(self) -> None:
        prop_datetime = Property(name="p5", type="DateTime", column_mapping="p5")
        self.assertEqual(cast_value(prop_datetime), "datetime(row.p5)")

    def test_cast_point(self) -> None:
        prop_point = Property(name="p6", type="CartesianPoint", column_mapping="p6")
        self.assertEqual(cast_value(prop_point), "point(row.p6)")

    def test_cast_integer(self) -> None:
        prop_int = Property(name="p2", type="int", column_mapping="p2")
        self.assertEqual(cast_value(prop_int), "toIntegerOrNull(row.p2)")

    def test_cast_float(self) -> None:
        prop_float = Property(name="p2", type="float", column_mapping="p2")
        self.assertEqual(cast_value(prop_float), "toFloatOrNull(row.p2)")

    def test_cast_bool(self) -> None:
        prop_bool = Property(name="p2", type="bool", column_mapping="p2")
        self.assertEqual(cast_value(prop_bool), "toBooleanOrNull(row.p2)")

    def test_cast_value_multi_column_mapping(self) -> None:
        prop_str = Property(name="p1", type="str", column_mapping="p1", alias="p1b")
        prop_point = Property(
            name="p1",
            type="neo4j.spatial.WGS84Point",
            column_mapping="p1",
            alias="p1b",
        )
        self.assertEqual(cast_value(prop_str), "row.p1")
        self.assertEqual(cast_value(prop_point), "point(row.p1)")

    def test_space_in_column_name(self) -> None:
        prop1 = Property(name="p1", type="str", column_mapping="p 1")

        self.assertEqual(cast_value(prop1), "row.`p 1`")

    def test_odd_characters_in_column_name(self) -> None:
        prop1 = Property(name="p#", type="str", column_mapping="#p")
        prop2 = Property(name="g", type="str", column_mapping="$g")

        self.assertEqual(cast_value(prop1), "row.`#p`")
        self.assertEqual(cast_value(prop2), "row.`$g`")


if __name__ == "__main__":
    unittest.main()
