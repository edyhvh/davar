import iconsData from "@/constants/icons.json";

export type IconKey = keyof typeof iconsData.icons;

export type IconSpec = {
  family: string;
  name: string;
  size: number;
  color: string;
  description?: string;
};

export const iconRegistry = iconsData.icons as Record<string, IconSpec>;

export const getIconSpec = (key: IconKey): IconSpec => iconRegistry[key];
