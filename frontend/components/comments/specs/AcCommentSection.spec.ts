import { Router, createRouter, createWebHistory } from "vue-router"
import { cleanUp, mount, rq, vueSetup, waitFor } from "@/specs/helpers/index.ts"
import { VueWrapper } from "@vue/test-utils"
import { ArtStore, createStore } from "@/store/index.ts"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import AcCommentSection from "@/components/comments/AcCommentSection.vue"
import mockAxios from "@/__mocks__/axios.ts"
import { commentSet as genCommentSet } from "@/components/comments/specs/fixtures.ts"
import { genUser } from "@/specs/helpers/fixtures.ts"
import { describe, expect, beforeEach, afterEach, test, vi } from "vitest"
import AcComment from "@/components/comments/AcComment.vue"
import { setViewer } from "@/lib/lib.ts"
import { nextTick } from "vue"

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe("AcCommentSection.vue", () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: "/",
          name: "Home",
          component: Empty,
        },
        {
          path: "/:username/",
          name: "Profile",
          component: Empty,
          children: [
            {
              path: "about",
              name: "AboutUser",
              component: Empty,
            },
          ],
        },
        {
          path: "/login/",
          name: "Login",
          component: Empty,
        },
      ],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  // This test appears to have some unknown isolation issue. It works on the second try.
  test("Fetches and renders a comment list", async () => {
    setViewer({ store, user: genUser() })
    const commentList = mount(Empty, vueSetup({ store })).vm.$getList(
      "commentList",
      {
        endpoint: "/api/comments/",
        reverse: true,
      },
    )
    wrapper = mount(AcCommentSection, {
      ...vueSetup({
        store,
        router,
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        showHistory: false,
        nesting: true,
        commentList,
      },
    })
    await nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/api/comments/", "get", undefined, {
        params: {
          page: 1,
          size: 24,
        },
        signal: expect.any(Object),
      }),
    )
    const commentSet = genCommentSet()
    commentList.makeReady(commentSet.results)
    commentList.response = commentSet
    // This might be 7 if AcNewComment loads, since it also uses that class name.
    await waitFor(() => expect(wrapper.findAll(".comment").length).toBe(6))
  })
  test("Throws an error if you try to load an unreversedlist", async () => {
    const commentList = mount(Empty, vueSetup({ store })).vm.$getList(
      "commentList",
      {
        endpoint: "/api/comments/",
      },
    )
    const mockError = vi.spyOn(console, "error")
    mockError.mockImplementationOnce(() => {})
    wrapper = mount(AcCommentSection, {
      ...vueSetup({
        store,
        router,
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        showHistory: true,
        commentList,
      },
    })
    expect(mockError).toHaveBeenCalledWith(
      "Comment lists should always be reversed!",
    )
  })
  test("Toggle history mode", async () => {
    setViewer({ store, user: genUser() })
    const commentList = mount(Empty, vueSetup({ store })).vm.$getList(
      "commentList",
      {
        endpoint: "/api/comments/",
        reverse: true,
      },
    )
    wrapper = mount(AcCommentSection, {
      ...vueSetup({
        store,
        router,
        components: {
          AcComment,
          AcCommentSection,
        },
      }),
      props: {
        showHistory: true,
        commentList,
      },
    })
    const vm = wrapper.vm as any
    await nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/api/comments/", "get", undefined, {
        signal: expect.any(Object),
        params: {
          page: 1,
          size: 24,
        },
      }),
    )
    mockAxios.reset()
    await wrapper.find(".comment-history-button").trigger("click")
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/api/comments/", "get", undefined, {
        params: {
          history: "1",
          page: 1,
          size: 24,
        },
        signal: expect.any(Object),
      }),
    )
    mockAxios.reset()
    await wrapper.find(".comment-history-button").trigger("click")
    await vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq("/api/comments/", "get", undefined, {
        signal: expect.any(Object),
        params: {
          page: 1,
          size: 24,
        },
      }),
    )
  })
})
