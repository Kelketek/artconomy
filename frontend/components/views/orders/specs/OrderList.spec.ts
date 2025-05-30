import {
  cleanUp,
  confirmAction,
  createTestRouter,
  mount,
  rs,
  waitFor,
  waitForSelector,
  vueSetup,
} from "@/specs/helpers/index.ts"
import { VueWrapper } from "@vue/test-utils"
import OrderList from "@/components/views/orders/OrderList.vue"
import mockAxios from "@/__mocks__/axios.ts"
import { genOrder, genProduct } from "@/specs/helpers/fixtures.ts"
import { afterEach, describe, expect, test, beforeEach } from "vitest"
import { Router } from "vue-router"
import { nextTick } from "vue"
import flushPromises from "flush-promises"
import { VDataTable } from "vuetify/lib/components/VDataTable/index.mjs"

let wrapper: VueWrapper<typeof OrderList>
let router: Router

describe("OrderList.vue", () => {
  beforeEach(() => {
    router = createTestRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Recognizes when it should show search functionality.", async () => {
    wrapper = mount(OrderList, {
      ...vueSetup({
        router,
      }),
      props: {
        type: "sales",
        category: "waiting",
        username: "Fox",
      },
    })
    const vm = wrapper.vm
    expect(vm.salesSearchable).toBe(true)
    await wrapper.setProps({ category: "archived" })
    await nextTick()
    expect(vm.salesSearchable).toBe(false)
    await wrapper.setProps({ category: "orders" })
    await nextTick()
    expect(vm.salesSearchable).toBe(false)
  })
  test("Loads state from query", async () => {
    await router.replace({
      query: {
        q: "lol",
        product: 10,
      },
    })
    wrapper = mount(OrderList, {
      ...vueSetup({
        router,
      }),
      props: {
        type: "sales",
        category: "waiting",
        username: "Fox",
      },
    })
    await nextTick()
    const vm = wrapper.vm as any
    expect(vm.showProduct).toBe(false)
    expect(vm.productInitItems.length).toBe(0)
    const request = mockAxios.getReqByUrl("/api/sales/account/Fox/products/10/")
    expect(request.method).toBe("get")
    mockAxios.mockResponse(
      rs(
        genProduct({
          id: 10,
          name: "stuff",
        }),
      ),
      request,
    )
    await nextTick()
    expect(vm.showProduct).toBe(true)
    expect(vm.productInitItems.length).toBe(1)
    expect(vm.productInitItems[0].name).toBe("stuff")
  })
  test("Clears a waitlist", async () => {
    wrapper = mount(OrderList, {
      ...vueSetup({ router }),
      props: {
        type: "sales",
        category: "waiting",
        username: "Fox",
      },
    })
    const vm = wrapper.vm
    vm.list.makeReady([])
    await nextTick()
    vm.searchForm.fields.product.update(100)
    await waitForSelector(wrapper, ".clear-waitlist:not([disabled])")
    await confirmAction(wrapper, [".clear-waitlist"])
    await nextTick()
    const request = mockAxios.getReqByUrl(
      "/api/sales/account/Fox/products/100/clear-waitlist/",
    )
    mockAxios.mockResponse(rs(undefined), request)
    await flushPromises()
    await nextTick()
    await waitFor(() => expect(vm.list.ready).toBe(false))
    // Force readiness to prevent promise issues as we close out.
    vm.list.kill()
    await nextTick()
  })
  test("Displays orders in a tabulated manner", async () => {
    wrapper = mount(OrderList, {
      ...vueSetup({
        router,
      }),
      props: {
        type: "sales",
        category: "waiting",
        username: "Fox",
      },
    })
    const vm = wrapper.vm as any
    vm.list.makeReady([
      genOrder({ id: 1 }),
      genOrder({
        id: 2,
        read: false,
      }),
      genOrder({
        id: 3,
        buyer: null,
      }),
    ])
    await nextTick()
    expect(wrapper.findComponent(VDataTable).exists()).toBeFalsy()
    vm.dataMode = true
    await nextTick()
    await waitFor(() =>
      expect(wrapper.findComponent(VDataTable).exists()).toBeTruthy(),
    )
  })
})
