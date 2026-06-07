"""
generate-mrt-test-boilerplate.py

Generate Jest+RTL test boilerplate for Material React Table components,
adapted for CRA 5's resetMocks: true default.

Produces:
- MRT mock with options capture
- Locale mock
- Supporting module mocks template
- renderApp helper
- Common assertion patterns

Usage:
  python3 generate-mrt-test-boilerplate.py --output <test-file-path>
  python3 generate-mrt-test-boilerplate.py --section mock --stdout
"""

import argparse
import textwrap
from typing import Optional


MRT_MOCK_SECTION = """
jest.mock("material-react-table/locales/en", () => ({ MRT_Localization_EN: {} }));

jest.mock("material-react-table", () => {
  const React = require("react");
  return {
    useMaterialReactTable: (options: any) => {
      mockTableOptions = options;
      return {
        ...options,
        columns: options.columns?.map((col: any) => ({
          ...col,
          getIsVisible: () => true,
          getSize: () => col.size || 150,
        })) || [],
        getAllColumns: () => (options.columns || []).map((col: any) => ({
          ...col,
          getIsVisible: () => true,
          getSize: () => col.size || 150,
        })),
        getState: () => ({
          isFullScreen: false,
          isSaving: false,
          showAlertBanner: false,
          showProgressBars: false,
          ...options.state,
        }),
        getRowModel: () => ({ rows: [] }),
        getIsSomeRowsSelected: () => false,
        getIsAllRowsSelected: () => false,
        getSelectedRowModel: () => ({ rows: [] }),
        resetRowSelection: () => {},
        resetColumnFilters: () => {},
        resetSorting: () => {},
        resetColumnVisibility: () => {},
        resetColumnOrder: () => {},
        resetColumnSizing: () => {},
        resetExpanded: () => {},
        resetGrouping: () => {},
        setRowSelection: () => {},
        setEditingRow: () => {},
        toggleAllRowsSelected: () => {},
      };
    },
    MaterialReactTable: ({ table }: any) => {
      return React.createElement("div", { "data-testid": "mrt-table" },
        table?.data?.map((row: any, i: number) =>
          React.createElement("div", {
            key: i,
            "data-testid": `mrt-row-${i}`,
            "data-exec-id": row.exec_id || "",
          },
            table?.columns?.map((col: any, j: number) => {
              const cellCtx = {
                cell: { getValue: () => row[col.accessorKey] },
                row: { original: row },
              };
              if (col.Cell) {
                return React.createElement("div", {
                  key: j,
                  "data-testid": `cell-${i}-${col.accessorKey || j}`,
                }, React.createElement(col.Cell, cellCtx));
              }
              return React.createElement("span", {
                key: j,
                "data-testid": `cell-${i}-${col.accessorKey || j}`,
              }, row[col.accessorKey] ?? "");
            })
          )
        )
      );
    },
  };
});
"""

HEADER_SECTION = """import "@testing-library/jest-dom";
import { render, screen, fireEvent, act } from '@testing-library/react';
import React from 'react';
"""

OPTIONS_VAR = """
var mockTableOptions: Record<string, any> = {};
"""

HELPERS_SECTION = """
const renderApp = (overrides: Record<string, any> = {}) => {
  return render(<App {...overrides} />);
};
"""

CONFIG_TESTS = """
  describe("Table Configuration Verification", () => {
    it("enableColumnFilters is true", () => { renderApp(); expect(mockTableOptions.enableColumnFilters).toBe(true); });
    it("enableDensityToggle is true", () => { renderApp(); expect(mockTableOptions.enableDensityToggle).toBe(true); });
    it("enableFullScreenToggle is true", () => { renderApp(); expect(mockTableOptions.enableFullScreenToggle).toBe(true); });
    it("enableColumnResizing is true", () => { renderApp(); expect(mockTableOptions.enableColumnResizing).toBe(true); });
    it("enableStickyHeader is true", () => { renderApp(); expect(mockTableOptions.enableStickyHeader).toBe(true); });
    it("enableColumnOrdering is true", () => { renderApp(); expect(mockTableOptions.enableColumnOrdering).toBe(true); });
    it("enableGrouping is true", () => { renderApp(); expect(mockTableOptions.enableGrouping).toBe(true); });
    it("manualSorting and manualPagination are true", () => { renderApp(); expect(mockTableOptions.manualSorting).toBe(true); expect(mockTableOptions.manualPagination).toBe(true); });
  });
"""


def generate_full_test(output_path: Optional[str] = None) -> str:
    parts = [
        HEADER_SECTION,
        OPTIONS_VAR,
        MRT_MOCK_SECTION,
        '\nimport App from "../Component";\n',
        HELPERS_SECTION,
        '\ndescribe("Component", () => {',
        '  beforeEach(() => { mockTableOptions = {}; });',
        CONFIG_TESTS,
        '});\n',
    ]
    return "\n\n".join(parts)


def generate_section(section_name: str) -> str:
    sections = {
        "mock": MRT_MOCK_SECTION.strip(),
        "header": HEADER_SECTION.strip(),
        "helpers": HELPERS_SECTION.strip(),
        "config-tests": CONFIG_TESTS.strip(),
    }
    return textwrap.dedent(sections.get(section_name, ""))


def main():
    parser = argparse.ArgumentParser(
        description="Generate MRT test boilerplate for CRA projects"
    )
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--section", type=str,
                        choices=["mock", "header", "helpers", "config-tests"],
                        help="Generate only a specific section")
    parser.add_argument("--stdout", action="store_true",
                        help="Print to stdout instead of saving")
    args = parser.parse_args()

    if args.section:
        content = generate_section(args.section)
    else:
        content = generate_full_test(args.output)

    if args.stdout or not args.output:
        print(content)
        return

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Written to {args.output}")


if __name__ == "__main__":
    main()
