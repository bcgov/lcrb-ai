import { Dropdown, IDropdownOption } from "@fluentui/react";

export type IndexSelectorProps = {
  selectedIndex: string;
  indexes: { name: string; value: string }[];
  onChange: (index: string) => void;
};

export const IndexSelector = ({
  selectedIndex,
  indexes,
  onChange,
}: IndexSelectorProps) => {
  const options: IDropdownOption[] = indexes.map(({ name, value }) => ({
    key: value,
    text: name,
  }));

  return (
    <Dropdown
      label="Channel Selector"
      selectedKey={selectedIndex}
      options={options}
      onChange={(_, option) => onChange(option?.key as string)}
      styles={{ dropdown: { width: 200 } }}
    />
  );
};
