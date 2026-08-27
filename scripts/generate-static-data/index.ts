/// <reference path="../../web/node_modules/@types/node/index.d.ts" />

import { createHash } from "crypto";
import { mkdir, readdir, readFile, rm, writeFile } from "fs/promises";
import { extname, join } from "path";
import {
  BUNDLE_VERSIONS,
  CANONICAL_BOOK_ORDER,
  DATA_ROOT,
  DELITZSCH_TO_ENGLISH,
  OE_TO_ENGLISH,
  WEB_PUBLIC_DATA_ROOT,
} from "./config";
import { VERSIFICATION_DATA } from "../../shared/versificationData";
