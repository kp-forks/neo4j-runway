from typing import List, Dict, Union, Any

from pydantic import BaseModel

from ..objects.arrows import ArrowsNode
from ..objects.property import Property


class Node(BaseModel):
    """
    Node representation.
    """

    label: str
    properties: List[Property] = []

    def __init__(self, label: str, properties: List[Property] = []) -> None:
        super().__init__(label=label, properties=properties)

    @property
    def property_names(self) -> List[str]:
        """
        The node's property names.
        """

        return [prop.name for prop in self.properties]

    @property
    def property_column_mapping(self) -> Dict[str, str]:
        """
        Map of properties to their respective csv columns.
        """

        return {prop.name: prop.csv_mapping for prop in self.properties}

    @property
    def unique_properties(self) -> List[str]:
        """
        The node's unique properties.
        """

        return [prop.name for prop in self.properties if prop.is_unique]

    @property
    def unique_properties_column_mapping(self) -> Dict[str, str]:
        """
        Map of unique properties to their respective csv columns.
        """

        return {
            prop.name: prop.csv_mapping for prop in self.properties if prop.is_unique
        }

    @property
    def nonunique_properties(self) -> List[str]:
        """
        The node's nonunique properties.
        """

        return [prop.name for prop in self.properties if not prop.is_unique]

    @property
    def nonunique_properties_column_mapping(self) -> Dict[str, str]:
        """
        Map of nonunique properties to their respective csv columns.
        """

        return {
            prop.name: prop.csv_mapping
            for prop in self.properties
            if not prop.is_unique
        }

    def validate_properties(self, csv_columns: List[str]) -> List[Union[str, None]]:
        errors = []
        if self.properties is not None:
            for prop in self.properties:
                if prop.csv_mapping not in csv_columns:
                    errors.append(
                        f"The node {self.label} has the property {prop.name} mapped to csv column {prop.csv_mapping} which does not exist. {prop} should be edited or removed from node {self.label}."
                    )
        return errors

    def to_arrows(self, x_position: float, y_position: float) -> ArrowsNode:
        """
        Return an arrows.app compatible node.
        """
        pos = {"x": x_position, "y": y_position}
        props = {x.name: x.csv_mapping + " | " + x.type for x in self.properties}
        caption = ", ".join([x.name for x in self.properties if x.is_unique])
        return ArrowsNode(
            id=self.label,
            caption=caption,
            position=pos,
            labels=[self.label],
            properties=props,
        )

    @classmethod
    def from_arrows(cls, arrows_node: ArrowsNode):
        """
        Initialize a Node from an arrows node.
        """

        props = [
            cls._parse_arrows_property(
                arrows_property={k: v}, arrows_node_caption=arrows_node.caption
            )
            for k, v in arrows_node.properties.items()
        ]
        # support only single labels for now, take first label
        return cls(label=arrows_node.labels[0], properties=props)

    @staticmethod
    def _parse_arrows_property(
        arrows_property: Dict[str, str], arrows_node_caption: str
    ) -> Property:
        """
        Parse the arrows property representation into a standard Property model.
        Unique property names are stored in the nodes caption as a comma-separated list: List<str>.
        Arrow property values are formatted as <csv_mapping> | <python_type>.
        """

        if "|" in list(arrows_property.values())[0]:
            csv_mapping, python_type = [
                x.strip() for x in list(arrows_property.values())[0].split("|")
            ]
        else:
            csv_mapping = list(arrows_property.values())[0]
            python_type = "unknown"

        is_unique = list(arrows_property.keys())[0] in [
            x.strip() for x in arrows_node_caption.split(",")
        ]

        return Property(
            name=list(arrows_property.keys())[0],
            csv_mapping=csv_mapping,
            type=python_type,
            is_unique=is_unique,
        )