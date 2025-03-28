import { VueWrapper } from "@vue/test-utils"
import { ArtStore, createStore } from "@/store/index.ts"
import {
  cleanUp,
  flushPromises,
  mount,
  rq,
  rs,
  vueSetup,
  VuetifyWrapped,
  waitForSelector,
} from "@/specs/helpers/index.ts"
import { genUser } from "@/specs/helpers/fixtures.ts"
import Empty from "@/specs/helpers/dummy_components/empty.ts"
import { commentSet as genCommentSet } from "./fixtures.ts"
import { Router, createRouter, createWebHistory } from "vue-router"
import mockAxios from "@/__mocks__/axios.ts"
import AcNewComment from "@/components/comments/AcNewComment.vue"
import { describe, expect, beforeEach, afterEach, test } from "vitest"
import { setViewer } from "@/lib/lib.ts"

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
let commentSet: ReturnType<typeof genCommentSet>

const WrappedNewComment = VuetifyWrapped(AcNewComment)

describe("AcNewComment.vue", () => {
  beforeEach(() => {
    store = createStore()
    commentSet = genCommentSet()
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
              path: "products",
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
  test("Posts a new comment", async () => {
    setViewer({ store, user: genUser() })
    const empty = mount(Empty, vueSetup({ store }))
    const commentList = empty.vm.$getList("commentList", {
      endpoint: "/api/comments/",
    })
    commentList.response = { ...commentSet }
    commentList.setList(commentSet.results)
    expect(commentList.list.length).toEqual(3)
    wrapper = mount(WrappedNewComment, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        commentList,
        extraData: { test: 1 },
      },
    })
    await waitForSelector(wrapper, "textarea")
    await wrapper.find("textarea").setValue("New comment!")
    await wrapper.vm.$nextTick()
    await wrapper.find(".submit-button").trigger("click")
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq(
        "/api/comments/",
        "post",
        {
          text: "New comment!",
          extra_data: { test: 1 },
        },
        {},
      ),
    )
    mockAxios.mockResponse(
      rs({
        id: 17,
        text: "New comment!",
        created_on: "2019-06-26T05:38:35.922476-05:00",
        edited_on: "2019-06-26T05:38:35.922499-05:00",
        user: {
          id: 3,
          username: "Fox",
          avatar_url:
            "https://www.gravatar.com/avatar/d3e61c0076b54b4cf19751e2cf8e17ed.jpg?s=80",
          stars: "4.25",
          is_staff: true,
          is_superuser: true,
          guest: false,
          artist_mode: null,
        },
        comments: [],
        comment_count: 0,
        edited: true,
        deleted: false,
        subscribed: true,
        system: false,
      }),
    )
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(commentList.list.length).toEqual(4)
  })
  test("Updates the extra data", async () => {
    setViewer({ store, user: genUser() })
    const empty = mount(Empty, vueSetup({ store }))
    const commentList = empty.vm.$getList("commentList", {
      endpoint: "/api/comments/",
    })
    commentList.response = { ...commentSet }
    commentList.setList(commentSet.results)
    expect(commentList.list.length).toEqual(3)
    wrapper = mount(WrappedNewComment, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        commentList,
        extraData: { test: 1 },
      },
    })
    await wrapper.setProps({
      extraData: { test: 3 },
    })
    await wrapper.find("textarea").setValue("New comment!")
    await wrapper.vm.$nextTick()
    await wrapper.find(".submit-button").trigger("click")
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq(
        "/api/comments/",
        "post",
        {
          text: "New comment!",
          extra_data: { test: 3 },
        },
        {},
      ),
    )
  })
})
