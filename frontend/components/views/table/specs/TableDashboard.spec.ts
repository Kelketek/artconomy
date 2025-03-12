import { createTestRouter, mount, vueSetup } from "@/specs/helpers/index.ts"
import TableDashboard from "@/components/views/table/TableDashboard.vue"
import { Router } from "vue-router"
import { beforeEach, describe, test } from "vitest"

let router: Router

describe("TableDashboard.vue", () => {
  beforeEach(() => {
    router = createTestRouter()
  })
  test("Mounts", async () => {
    await router.push({ name: "TableDashboard" })
    mount(TableDashboard, vueSetup())
  })
})
