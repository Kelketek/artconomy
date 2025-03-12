import { formRegistry } from "../registry.ts"
import { axiosCatch, FieldController } from "../field-controller.ts"
import { FormController } from "../form-controller.ts"
import { ArtStore, createStore } from "@/store/index.ts"
import { mount, shallowMount, VueWrapper } from "@vue/test-utils"
import mockAxios from "@/specs/helpers/mock-axios.ts"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import flushPromises from "flush-promises"
import ErrorScrollTests from "@/specs/helpers/dummy_components/scroll-tests.vue"
import { cleanUp, docTarget, vueSetup } from "@/specs/helpers/index.ts"
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest"
import { nextTick } from "vue"
import { createRouter, createWebHistory, Router } from "vue-router"
import { singleRegistry } from "@/store/singles/registry.ts"
import { listRegistry } from "@/store/lists/registry.ts"
import { characterRegistry } from "@/store/characters/registry.ts"
import { RegistryRegistry } from "@/store/registry-base.ts"
import { profileRegistry } from "@/store/profiles/registry.ts"
import { buildSocketManger, SocketManager } from "@/plugins/socket.ts"
import { RootFormState } from "@/store/forms/types/main"

const mockScrollIntoView = (Element.prototype.scrollIntoView = vi.fn())

function min(
  field: FieldController,
  minimum: number,
  message?: string,
): string[] {
  if (field.value < minimum) {
    return [message || "Too low."]
  }
  return []
}

async function alwaysFail(
  field: FieldController,
  signal: AbortSignal,
  arg: string,
) {
  expect(arg).toEqual("test")
  return new Promise<string[]>((resolve) => resolve(["I failed!"]))
}

// noinspection JSUnusedLocalSymbols
async function alwaysSucceed() {
  return new Promise<string[]>((resolve) => resolve([]))
}

const mockError = vi.spyOn(console, "error")
const mockTrace = vi.spyOn(console, "trace")

describe("Form and field controllers", () => {
  let store: ArtStore
  let state: RootFormState
  let wrapper: VueWrapper<any>
  let router: Router
  let socket: SocketManager
  const registries: RegistryRegistry = {
    Form: formRegistry,
    Single: singleRegistry,
    List: listRegistry,
    Character: characterRegistry,
    Profile: profileRegistry,
  }
  beforeEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
    store = createStore()
    state = (store.state as any).forms as RootFormState
    mockError.mockClear()
    mockTrace.mockClear()
    router = createRouter({
      history: createWebHistory(),
      routes: [{ name: "Home", path: "/", component: Empty }],
    })
    mockScrollIntoView.mockClear()
    formRegistry.resetValidators()
    formRegistry.reset()
    socket = buildSocketManger({ endpoint: "/beep/" })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test("Initializes a form controller", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        errors: ["Borked."],
        fields: {
          name: {
            value: "Fox",
            errors: ["Too cool."],
          },
          age: { value: 30 },
        },
      },
    })
    expect(controller.name.value).toBe("example")
    expect(controller.purged).toBe(false)
    expect(controller.fields).toBeTruthy()
    expect(controller.fields.name).toBeTruthy()
    expect(controller.fields.name.fieldName).toBe("name")
    expect(controller.fields.name.formName).toBe("example")
    expect(controller.fields.age.fieldName).toBe("age")
    expect(controller.fields.age.formName).toBe("example")
    expect(controller.errors).toEqual(["Borked."])
    expect(state.example.fields.name.initialData).toBe("Fox")
    expect(state.example.method).toBe("post")
    expect(state.example.fields.age.initialData).toBe(30)
  })
  test("Submits a form through a FormController", async () => {
    const success = vi.fn()
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    controller.submitThen(success).then()
    mockAxios.mockResponse({
      status: 200,
      data: { test: "result" },
    })
    await flushPromises()
    expect(success).toBeCalled()
    expect(success).toBeCalledWith({ test: "result" })
  })
  test("Allows manual toggle of sending status", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    controller.sending = true
    expect(state.example.sending).toBe(true)
    controller.sending = false
    expect(state.example.sending).toBe(false)
  })
  test("Clears errors", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        errors: ["Too amazing"],
        fields: {
          name: {
            value: "Fox",
            errors: ["Too cool."],
          },
          age: { value: 30 },
        },
      },
    })
    expect(state.example.errors).toEqual(["Too amazing"])
    expect(state.example.fields.name.errors).toEqual(["Too cool."])
    controller.clearErrors()
    expect(state.example.errors).toEqual([])
    expect(state.example.fields.name.errors).toEqual([])
  })
  test("Recognizes failed steps", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        errors: ["Too amazing"],
        fields: {
          name: {
            value: "Fox",
            errors: ["Too cool."],
          },
          age: {
            value: 30,
            errors: ["Wat"],
            step: 2,
          },
          things: {
            value: "",
            step: 3,
          },
        },
      },
    })
    expect(state.example.errors).toEqual(["Too amazing"])
    expect(state.example.fields.name.errors).toEqual(["Too cool."])
    expect(controller.failedSteps).toEqual([1, 2])
  })
  test("Sets field-specific errors upon a failed request", async () => {
    const success = vi.fn()
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 20 },
        },
      },
    })
    controller.submitThen(success).then()
    store.dispatch("forms/submit", { name: "example" }).then()
    mockAxios.mockError!({
      response: { data: { age: ["You stopped being 20 a long time ago."] } },
    })
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([
      "You stopped being 20 a long time ago.",
    ])
    expect(controller.fields.name.errors).toEqual([])
  })
  test("Sets the right step upon a failed request", async () => {
    const success = vi.fn()
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: {
            value: 20,
            step: 2,
          },
          stuff: {
            value: 2,
            step: 3,
          },
        },
      },
    })
    controller.step = 3
    expect(controller.step).toBe(3)
    controller.submitThen(success).then()
    store.dispatch("forms/submit", { name: "example" }).then()
    mockAxios.mockError!({
      response: { data: { age: ["You stopped being 20 a long time ago."] } },
    })
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.step).toBe(2)
  })
  test("Sets a general error upon a failed request", async () => {
    const success = vi.fn()
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 20 },
        },
      },
    })
    controller.submitThen(success).then()
    store.dispatch("forms/submit", { name: "example" }).then()
    mockTrace.mockImplementationOnce(() => undefined)
    mockAxios.mockError!({})
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([])
    expect(controller.errors).toEqual([
      "We had an issue contacting the server. Please try again later!",
    ])
    expect(mockTrace).toHaveBeenCalled()
  })
  test("Sets a general error upon a DRF error message", async () => {
    const success = vi.fn()
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 20 },
        },
      },
    })
    controller.submitThen(success).then()
    store.dispatch("forms/submit", { name: "example" }).then()
    mockAxios.mockError!({
      response: { data: { detail: "This is a thing." } },
    })
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([])
    expect(controller.errors).toEqual(["This is a thing."])
  })
  test("Sets a general errors upon array error messages", async () => {
    const success = vi.fn()
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 20 },
        },
      },
    })
    controller.submitThen(success).then()
    store.dispatch("forms/submit", { name: "example" }).then()
    mockAxios.mockError!({ response: { data: ["This is a thing."] } })
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([])
    expect(controller.errors).toEqual(["This is a thing."])
  })
  test("Sets general errors upon a non-json error response", async () => {
    const success = vi.fn()
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 20 },
        },
      },
    })
    controller.submitThen(success).then()
    store.dispatch("forms/submit", { name: "example" }).then()
    mockTrace.mockImplementationOnce(() => undefined)
    mockAxios.mockError!({ response: { data: "Stuff" } })
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([])
    expect(controller.errors).toEqual([
      "We had an issue contacting the server. Please try again later!",
    ])
    expect(mockTrace).toHaveBeenCalled()
  })
  test("Lets us know if we forgot a field", async () => {
    const success = vi.fn()
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 20 },
        },
      },
    })
    controller.submitThen(success).then()
    store.dispatch("forms/submit", { name: "example" }).then()
    mockAxios.mockError!({
      response: { data: { other_field: ["You forgot me."] } },
    })
    await flushPromises()
    expect(success).toHaveBeenCalledTimes(0)
    expect(controller.fields.age.value).toBe(20)
    expect(controller.fields.age.errors).toEqual([])
    expect(controller.errors).toEqual([
      "Whoops! We had a coding error. Please contact support and tell them the following: " +
        "other_field: You forgot me.",
    ])
  })
  test("Adds a field to the FormController when the schema is updated", () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    store.commit("forms/addField", {
      name: "example",
      field: {
        name: "sex",
        schema: { value: "Male" },
      },
    })
    expect(controller.fields.sex).toBeTruthy()
    expect(controller.fields.sex.fieldName).toBe("sex")
    expect(controller.fields.sex.formName).toBe("example")
  })
  test("Does not add a field to the FormController when a different form is updated", () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
        errors: ["Borked."],
      },
    })

    new FormController({
      $store: store,
      initName: "example2",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
        errors: ["Borked."],
      },
    })
    store.commit("forms/addField", {
      name: "example2",
      field: {
        name: "sex",
        schema: { value: "Male" },
      },
    })
    expect(controller.fields.sex).toBe(undefined)
  })
  test("Removes a field from the FormController when the schema is updated", () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    store.commit("forms/delField", {
      name: "example",
      field: "age",
    })
    expect(controller.fields.age).toBe(undefined)
  })
  test("Does not remove a field from the FormController when deleting from a different form.", () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: {
            value: "Fox",
            errors: ["Too cool."],
          },
          age: { value: 30 },
        },
      },
    })

    new FormController({
      $store: store,
      initName: "example2",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: {
            value: "Fox",
            errors: ["Too cool."],
          },
          age: { value: 30 },
        },
      },
    })
    store.commit("forms/delField", {
      name: "example2",
      field: "age",
    })
    expect(controller.fields.age).toBeTruthy()
  })
  test("Handles deletion of the form in a FormController", () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    store.commit("forms/delForm", { name: "example" })
    expect(Object.keys(controller.fields)).toEqual([])
    expect(controller.purged).toBe(true)
    expect(controller.errors).toEqual([])
  })
  test("Doesn't self-delete if deleting a different form", () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    store.commit("forms/delForm", { name: "example2" })
    expect(Object.keys(controller.fields)).toBeTruthy()
    expect(controller.purged).toBe(false)
  })
  test("Updates the endpoint of the form", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {},
      },
    })
    expect(state.example.endpoint).toBe("/endpoint/")
    controller.endpoint = "/wat/"
    expect(state.example.endpoint).toBe("/wat/")
  })
  test("Retrieves an attribute of a form", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {},
      },
    })
    expect(controller.attr("endpoint")).toBe("/endpoint/")
  })
  test("Retrieves calculated data from a form", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          stuff: { value: "things" },
          wat: {
            value: "do",
            omitIf: "do",
          },
          goober: { value: 100 },
        },
      },
    })
    expect(controller.rawData).toEqual({
      stuff: "things",
      goober: 100,
    })
  })
  test("Allows deletion of the form through a FormController", () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    expect(state.example).toBeTruthy()
    expect(formRegistry.controllers).toBeTruthy()
    controller.purge()
    expect(state.example).toBe(undefined)
    const result = { ...formRegistry.controllers }
    delete result.__ob__
    expect(result).toEqual({})
    expect(Object.keys(controller.fields)).toEqual([])
    expect(controller.purged).toBe(true)
  })
  test("Scrolls to errors in scrollable text", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    wrapper = mount(ErrorScrollTests, {
      ...vueSetup({ store }),
      props: { test: "scrollableText" },
    })
    await wrapper.vm.$nextTick()
    const element = document.querySelector("#scrollable-text-error") as Element
    controller.scrollToError()
    expect(element.scrollIntoView).toHaveBeenCalledWith({
      behavior: "smooth",
      block: "center",
    })
  })
  test("Scrolls to errors in ID only", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    wrapper = mount(ErrorScrollTests, {
      ...vueSetup({ store }),
      props: { test: "idOnly" },
    })
    await wrapper.vm.$nextTick()
    const element = document.querySelector("#id-only-error") as Element
    controller.scrollToError()
    expect(element.scrollIntoView).toHaveBeenCalledWith({
      behavior: "smooth",
      block: "center",
    })
  })
  test("Does not break if there are no errors in the form ID when attempting to scroll", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    wrapper = shallowMount(ErrorScrollTests, {
      test: "noError",
      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    controller.scrollToError()
    expect(Element.prototype.scrollIntoView).not.toHaveBeenCalled()
  })
  test("Does not break if there is no form to scroll to", async () => {
    const controller = new FormController({
      $store: store,
      initName: "example",
      $router: router,
      $registries: registries,
      $sock: socket,
      schema: {
        endpoint: "/endpoint/",
        fields: {
          name: { value: "Fox" },
          age: { value: 30 },
        },
      },
    })
    wrapper = shallowMount(ErrorScrollTests, {
      test: "noErrorNoId",
      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    controller.scrollToError()
    expect(Element.prototype.scrollIntoView).not.toHaveBeenCalled()
  })
  test("Initializes a field controller", () => {
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          errors: ["Too cool."],
        },
        age: { value: 30 },
      },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $store: store,
      formName: "example",
      fieldName: "name",
      $router: router,
      $registries: registries,
      $sock: socket,
    })
    expect(controller.fieldName).toBe("name")
    expect(controller.formName).toBe("example")
    expect(controller.value).toBe("Fox")
    expect(controller.errors).toEqual(["Too cool."])
  })
  test("Updates a field", async () => {
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          errors: ["Too cool."],
        },
        age: { value: 30 },
      },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "name",
    })
    expect(controller.fieldName).toBe("name")
    expect(controller.formName).toBe("example")
    expect(controller.value).toBe("Fox")
    expect(controller.errors).toEqual(["Too cool."])
    controller.update("Amber")
    controller.validate.flush()
    await flushPromises()
    expect(state.example.fields.name.value).toBe("Amber")
    expect(controller.value).toBe("Amber")
    expect(controller.errors).toEqual([])
  })
  test("Produces field bindings", () => {
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          errors: ["Too cool."],
          extra: { checked: true },
        },
        age: { value: 30 },
      },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "name",
    })
    expect(controller.bind).toEqual({
      modelValue: "Fox",
      errorMessages: ["Too cool."],
      disabled: false,
      checked: true,
      id: "field-example__name",
      onBlur: controller.forceValidate,
      "onUpdate:modelValue": controller.update,
    })
    expect(controller.rawBind).toEqual({
      value: "Fox",
      disabled: false,
      checked: true,
      id: "field-example__name",
      onBlur: controller.forceValidate,
      onInput: controller.domUpdate,
      onChange: controller.domUpdate,
    })
  })
  test("Retrieves attributes", () => {
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          errors: ["Too cool."],
          disabled: true,
        },
        age: { value: 30 },
      },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "name",
    })
    expect(controller.attr("disabled")).toBe(true)
  })
  test("Uses the debounce rate of the form by default", () => {
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          errors: ["Too cool."],
          disabled: true,
        },
        age: { value: 30 },
      },
      debounce: 500,
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "name",
    })
    expect(controller.debounceRate).toBe(500)
  })
  test("Allows override of the debounce rate per field", () => {
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          errors: ["Too cool."],
          disabled: true,
          debounce: 200,
        },
        age: { value: 30 },
      },
      debounce: 500,
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "name",
    })
    expect(controller.debounceRate).toBe(200)
  })
  test("Validates a field", async () => {
    formRegistry.validators.min = min
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          disabled: true,
        },
        age: {
          value: 20,
          validators: [
            {
              name: "min",
              args: [30],
            },
            {
              name: "min",
              args: [25, "You've got to be at least 25."],
            },
          ],
          errors: ["Old error"],
        },
      },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "age",
    })
    expect(controller.errors).toEqual(["Old error"])
    controller.forceValidate()
    await flushPromises()
    expect(controller.errors).toEqual([
      "Too low.",
      "You've got to be at least 25.",
    ])
  })
  test("Returns validators", async () => {
    formRegistry.validators.min = min
    const validators = [
      {
        name: "min",
        args: [30],
      },
      {
        name: "min",
        args: [25, "You've got to be at least 25."],
      },
    ]
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          disabled: true,
        },
        age: {
          value: 20,
          validators,
          errors: ["Old error"],
        },
      },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "age",
    })
    expect(controller.validators).toEqual(validators)
  })
  test("Updates a field without validation", () => {
    formRegistry.validators.min = min
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          disabled: true,
        },
        age: {
          value: 30,
          validators: [
            {
              name: "min",
              args: [30],
            },
            {
              name: "min",
              args: [25, "You've got to be at least 25."],
            },
          ],
          errors: ["Old error"],
        },
      },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "age",
    })
    expect(controller.errors).toEqual(["Old error"])
    controller.update(20, false)
    expect(controller.errors).toEqual(["Old error"])
  })
  test("Exposes a field as a model", async () => {
    store.commit("forms/initForm", {
      name: "example",
      fields: { name: { value: "Fox" } },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "name",
    })
    expect(state.example.fields.name.value).toBe("Fox")
    expect(controller.model).toBe("Fox")
    controller.model = "Amber"
    await nextTick()
    expect(state.example.fields.name.value).toBe("Amber")
    expect(controller.model).toBe("Amber")
  })
  test("Runs async validators", async () => {
    formRegistry.validators.min = min
    formRegistry.asyncValidators.alwaysFail = alwaysFail
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          disabled: true,
        },
        age: {
          value: 20,
          validators: [
            {
              name: "min",
              args: [30],
            },
            {
              name: "min",
              args: [25, "You've got to be at least 25."],
            },
            {
              name: "alwaysFail",
              args: ["test"],
              async: true,
            },
          ],
          errors: ["Old error"],
        },
      },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "age",
    })
    controller.forceValidate()
    await flushPromises()
    expect(controller.errors).toEqual([
      "Too low.",
      "You've got to be at least 25.",
      "I failed!",
    ])
  })
  test("Gets and sets initial data on a field", async () => {
    formRegistry.validators.min = min
    formRegistry.asyncValidators.alwaysFail = alwaysFail
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: { value: "Fox" },
        age: {
          value: 20,
        },
      },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "age",
    })
    expect(controller.initialData).toBe(20)
    controller.initialData = 15
    expect(state.example.fields.age.initialData).toBe(15)
  })
  test("Gives useful error message on unknown sync validator", async () => {
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          disabled: true,
        },
        age: {
          value: 30,
          validators: [
            {
              name: "min",
              args: [30],
            },
          ],
        },
      },
      endpoint: "/test/endpoint/",
    })
    formRegistry.validators.max = min
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "age",
    })
    mockError.mockImplementationOnce(() => undefined)
    controller.forceValidate()
    expect(mockError).toHaveBeenCalledTimes(1)
    expect(mockError).toHaveBeenCalledWith(
      "Unregistered synchronous validator: ",
      "min",
      "\n",
      "Options are: ",
      ["max"],
    )
  })
  test("Gives useful error message on unknown async validator", async () => {
    store.commit("forms/initForm", {
      name: "example",
      fields: {
        name: {
          value: "Fox",
          disabled: true,
        },
        age: {
          value: 30,
          validators: [
            {
              name: "min",
              async: true,
            },
            {
              name: "alwaysSucceed",
              async: true,
            },
          ],
        },
      },
      endpoint: "/test/endpoint/",
    })
    formRegistry.asyncValidators.alwaysSucceed = alwaysSucceed
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "age",
    })
    mockError.mockImplementationOnce(() => undefined)
    controller.forceValidate()
    expect(mockError).toHaveBeenCalledTimes(1)
    expect(mockError).toHaveBeenCalledWith(
      "Unregistered asynchronous validator: ",
      "min",
      "\n",
      "Options are: ",
      ["alwaysSucceed"],
    )
  })
  test("Retrieves the parent form controller", () => {
    wrapper = shallowMount(Empty, vueSetup({ store }))
    const controller = wrapper.vm.$getForm("example", {
      fields: {
        age: { value: 30 },
      },
      endpoint: "/test/endpoint/",
    })
    const fieldController = controller.fields.age
    expect(fieldController.form).toBe(controller)
  })
  test("Correctly identifies an axios cancellation and ignores it.", async () => {
    mockTrace.mockImplementationOnce(() => undefined)
    const error = new Error("Request cancelled.")
    ;(error as any).__CANCEL__ = true
    axiosCatch(error)
    expect(mockTrace).toHaveBeenCalledTimes(0)
  })
  test("Correctly identifies a non-axios cancellation and complains about it.", async () => {
    mockTrace.mockImplementationOnce(() => undefined)
    const error = new Error("Failed!")
    axiosCatch(error)
    expect(mockTrace).toHaveBeenCalledTimes(1)
  })
  test("Resets the form", () => {
    wrapper = shallowMount(Empty, vueSetup({ store }))
    const controller = wrapper.vm.$getForm("example", {
      fields: {
        age: { value: 30 },
      },
      endpoint: "/test/endpoint/",
    })
    controller.fields.age.update(31)
    expect(controller.fields.age.value).toBe(31)
    controller.reset()
    expect(controller.fields.age.value).toBe(30)
  })
  test("Simplifies JSON rendering", () => {
    wrapper = shallowMount(Empty, vueSetup({ store }))
    const controller = wrapper.vm.$getForm("example", {
      fields: {
        age: { value: 30 },
      },
      endpoint: "/test/endpoint/",
    })
    expect(JSON.parse(JSON.stringify(controller))).toEqual({
      type: "FormController",
      state: { age: 30 },
      name: "example",
    })
    expect(JSON.parse(JSON.stringify(controller.fields.age))).toEqual({
      type: "FieldController",
      state: 30,
      name: "age",
    })
  })
  test("Makes a sane, consistent CSS name", () => {
    wrapper = shallowMount(Empty, vueSetup({ store }))
    wrapper.vm.$getForm("example", {
      fields: {
        "@beep": { value: 30 },
      },
      endpoint: "/test/endpoint/",
    })
    const controller = new FieldController({
      $router: router,
      $registries: registries,
      $store: store,
      $sock: socket,
      formName: "example",
      fieldName: "@beep",
    })
    expect(controller.id).toBe("field-example__\\@beep")
  })
})
