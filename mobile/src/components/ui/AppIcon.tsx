import {
  AntDesign,
  Entypo,
  Feather,
  FontAwesome,
  FontAwesome5,
  FontAwesome6,
  Fontisto,
  Ionicons,
  MaterialCommunityIcons,
  MaterialIcons,
} from "@expo/vector-icons";
import React from "react";

import { getIconSpec, type IconKey } from "@/src/constants/icons";

const familyMap = {
  AntDesign,
  Entypo,
  Feather,
  FontAwesome,
  FontAwesome5,
  FontAwesome6,
  Fontisto,
  Ionicons,
  MaterialCommunityIcons,
  MaterialIcons,
} as const;

type AppIconProps = {
  name: IconKey;
  size?: number;
  color?: string;
};

export const AppIcon = ({ name, size, color }: AppIconProps) => {
  const spec = getIconSpec(name);
  const IconComponent = familyMap[spec.family as keyof typeof familyMap];

  if (!IconComponent) {
    return null;
  }

  return (
    <IconComponent
      name={spec.name as never}
      size={size ?? spec.size}
      color={color ?? spec.color}
    />
  );
};
