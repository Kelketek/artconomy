<template>
  <v-container v-if="subject" fluid style="min-height: 75vh" role="navigation">
    <v-list density="compact" nav role="list">
      <v-list-item
        role="listitem"
        tabindex="0"
        @click="emit('update:modelValue', false)"
      >
        <template #prepend>
          <v-icon :icon="mdiClose" />
        </template>
        <v-list-item-title>Close Menu</v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="showSfwToggle"
        class="hidden-sm-and-up"
        role="listitem"
        tabindex="0"
      >
        <ac-patch-field
          field-type="v-switch"
          :patcher="sfwMode"
          :save-indicator="false"
          label="SFW Mode"
          color="primary"
        />
      </v-list-item>
      <v-list-item to="/" exact role="listitem" tabindex="0">
        <template #prepend>
          <v-icon :icon="mdiHome" />
        </template>
        <v-list-item-title>Home</v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="!isRegistered"
        :to="{ name: 'SessionSettings' }"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiCog" />
        </template>
        <v-list-item-title>Settings</v-list-item-title>
      </v-list-item>
      <v-list-item
        :to="{name: 'Calculator'}"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiCalculator" />
        </template>
        <v-list-item-title>Calculator</v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="isRegistered"
        :to="{ name: 'Conversations', params: { username: subject.username } }"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiEmail" />
        </template>
        <v-list-item-title>Private Messages</v-list-item-title>
      </v-list-item>
    </v-list>
    <v-list
      v-if="isLoggedIn && subject.artist_mode"
      v-model:opened="openSecond"
      nav
      density="compact"
      open-strategy="multiple"
      role="list"
      tabindex="0"
    >
      <v-divider aria-hidden="true" />
      <v-list-item
        :to="{ name: 'Store', params: { username: subject.username } }"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiStorefront" />
        </template>
        <v-list-item-title>My Store</v-list-item-title>
      </v-list-item>
      <v-list-item
        :to="{ name: 'CurrentSales', params: { username: subject.username } }"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiCashMultiple" />
        </template>
        <v-list-item-title>Sales/Invoicing</v-list-item-title>
      </v-list-item>
      <v-list-group
        v-if="
          isLoggedIn &&
          (powers.view_financials ||
            powers.view_social_data ||
            powers.handle_disputes)
        "
        value="Reports"
        nav
        role="listitem"
      >
        <template #activator="activator">
          <v-list-item v-bind="activator.props" tabindex="0">
            <v-list-item-title>Reports</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item
          :to="{ name: 'Reports', params: { username: subject.username } }"
          role="listitem"
          tabindex="0"
        >
          <template #prepend>
            <v-icon :icon="mdiChartBoxOutline" />
          </template>
          <v-list-item-title>Financial</v-list-item-title>
        </v-list-item>
        <v-list-item
          v-if="powers.handle_disputes"
          :to="{ name: 'TroubledDeliverables' }"
          role="listitem"
          tabindex="0"
        >
          <template #prepend>
            <v-icon :icon="mdiAlert" />
          </template>
          <v-list-item-title>Troubled Deliverables</v-list-item-title>
        </v-list-item>
        <v-list-item
          v-if="powers.view_social_data"
          :to="{ name: 'Promotable' }"
          role="listitem"
          tabindex="0"
        >
          <template #prepend>
            <v-icon :icon="mdiBullhorn" />
          </template>
          <v-list-item-title>Promotable Artists</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item
        v-else-if="
          isLoggedIn && (powers.view_financials || powers.table_seller)
        "
        :to="{ name: 'Reports', params: { username: subject.username } }"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiChartBoxOutline" />
        </template>
        <v-list-item-title>Reports</v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="isLoggedIn && powers.table_seller"
        :to="{ name: 'TableProducts' }"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiStoreCogOutline" />
        </template>
        <v-list-item-title>Table Dashboard</v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="isLoggedIn && powers.view_financials"
        :to="{ name: 'VendorInvoices' }"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiInvoice" />
        </template>
        <v-list-item-title>Vendor Invoices</v-list-item-title>
      </v-list-item>
      <v-divider aria-hidden="true" />
    </v-list>
    <v-list
      v-if="powers.handle_disputes"
      nav
      density="compact"
      role="list"
      tabindex="0"
    >
      <v-list-item
        :to="{ name: 'CurrentCases', params: { username: subject.username } }"
        role="listitem"
      >
        <template #prepend>
          <v-icon :icon="mdiGavel" />
        </template>
        <v-list-item-title>Cases</v-list-item-title>
      </v-list-item>
    </v-list>
    <v-list
      v-model:opened="openFirst"
      density="compact"
      nav
      open-strategy="multiple"
      role="list"
    >
      <v-list-item
        v-if="isLoggedIn"
        :to="{ name: 'CurrentOrders', params: { username: subject.username } }"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiBasket" />
        </template>
        <v-list-item-title>Orders</v-list-item-title>
      </v-list-item>
      <v-list-group v-if="isRegistered" value="Openings" nav role="listitem">
        <template #activator="activator">
          <v-list-item v-bind="activator.props" tabindex="0" role="listitem">
            <v-list-item-title>Who's Open?</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item
          :to="{ name: 'SearchProducts' }"
          role="listitem"
          tabindex="0"
          @click.capture.stop.prevent="searchOpen({})"
        >
          <template #prepend>
            <v-icon class="who-is-open" :icon="mdiCity" />
          </template>
          <v-list-item-title>All Openings</v-list-item-title>
        </v-list-item>
        <v-list-item
          exact
          :to="{ name: 'SearchProducts', query: { watch_list: 'true' } }"
          tabindex="0"
          role="listitem"
          @click.capture.stop.prevent="searchOpen({ watch_list: true })"
        >
          <template #prepend>
            <v-icon class="who-is-open-watchlist" :icon="mdiStore" />
          </template>
          <v-list-item-title>Watchlist</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item
        v-else
        exact
        :to="{ name: 'SearchProducts' }"
        role="listitem"
        tabindex="0"
        @click.capture.stop.prevent="searchOpen({})"
      >
        <template #prepend>
          <v-icon class="who-is-open" :icon="mdiStore" />
        </template>
        <v-list-item-title>Who's Open?</v-list-item-title>
      </v-list-item>
      <v-list-group v-if="isRegistered" nav value="Art" role="listitem">
        <template #activator="activator">
          <v-list-item v-bind="activator.props" tabindex="0" role="listitem">
            <v-list-item-title>Recent Art</v-list-item-title>
          </v-list-item>
        </template>
        <v-list-item
          :exact="true"
          :to="{ name: 'SearchSubmissions' }"
          role="listitem"
          tabindex="0"
          @click.capture.stop.prevent="searchSubmissions({})"
        >
          <template #prepend>
            <v-icon class="recent-art" :icon="mdiImageMultiple" />
          </template>
          <v-list-item-title>All Submissions</v-list-item-title>
        </v-list-item>
        <v-list-item
          :exact="true"
          :to="{ name: 'SearchSubmissions', query: { watch_list: 'true' } }"
          role="listitem"
          tabindex="0"
          @click.capture.stop.prevent="searchSubmissions({ watch_list: true })"
        >
          <template #prepend>
            <v-icon class="recent-art-watchlist" :icon="mdiEye" />
          </template>
          <v-list-item-title>Watchlist</v-list-item-title>
        </v-list-item>
      </v-list-group>
      <v-list-item
        v-else
        :to="{ name: 'SearchSubmissions' }"
        role="listitem"
        tabindex="0"
        @click.capture.stop.prevent="searchSubmissions({})"
      >
        <template #prepend>
          <v-icon class="recent-art" :icon="mdiImageMultiple" />
        </template>
        <v-list-item-title>Recent Art</v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="isRegistered"
        :to="{ name: 'LinksAndStats', params: { username: subject.username } }"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiStar" />
        </template>
        <v-list-item-title> Extras! </v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="isRegistered && !embedded"
        :to="{ name: 'Upgrade', params: { username: subject.username } }"
        role="listitem"
        tabindex="0"
      >
        <template #prepend>
          <v-icon :icon="mdiArrowUp" />
        </template>
        <v-list-item-title> Upgrade </v-list-item-title>
      </v-list-item>
    </v-list>
    <v-divider aria-hidden="true" />
    <v-list nav density="compact" role="list">
      <v-list-group
        v-if="isRegistered"
        :prepend-icon="mdiCog"
        value="Settings"
        role="listitem"
      >
        <template #activator="activator">
          <v-list-item v-bind="activator.props" tabindex="0">
            <v-list-item-title>Settings</v-list-item-title>
          </v-list-item>
        </template>
        <ac-setting-nav :username="subject.username" :nested="true" />
      </v-list-group>
      <v-list-item
        v-if="!embedded"
        :to="{ name: 'About' }"
        tabindex="0"
        role="listitem"
      >
        <template #prepend>
          <v-icon :icon="mdiForum" />
        </template>
        <v-list-item-title>FAQ</v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="isRegistered && !embedded"
        tabindex="0"
        role="listitem"
        @click.prevent="logout()"
      >
        <template #prepend>
          <v-icon class="logout-button" :icon="mdiLogout" />
        </template>
        <v-list-item-title>Log out</v-list-item-title>
      </v-list-item>
      <v-list-item
        v-if="!embedded"
        class="mt-3"
        :to="{ name: 'Policies' }"
        tabindex="0"
        role="listitem"
      >
        <template #prepend>
          <v-icon :icon="mdiInformation" />
        </template>
        <v-list-item-title>Privacy and Legal</v-list-item-title>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script setup lang="ts">
import AcSettingNav from "@/components/navigation/AcSettingNav.vue"
import { ProfileController } from "@/store/profiles/controller.ts"
import AcPatchField from "@/components/fields/AcPatchField.vue"
import { artCall, makeQueryParams } from "@/lib/lib.ts"
import { computed, ref, watch } from "vue"
import { useForm } from "@/store/forms/hooks.ts"
import { useRouter } from "vue-router"
import {
  mdiAlert,
  mdiArrowUp,
  mdiBasket,
  mdiBullhorn, mdiCalculator,
  mdiCashMultiple,
  mdiChartBoxOutline,
  mdiCity,
  mdiClose,
  mdiCog,
  mdiEmail,
  mdiEye,
  mdiForum,
  mdiGavel,
  mdiHome,
  mdiImageMultiple,
  mdiInformation,
  mdiInvoice,
  mdiLogout,
  mdiStar,
  mdiStore,
  mdiStoreCogOutline,
  mdiStorefront
} from "@mdi/js"
import { buildPowers, useViewer } from "@/mixins/viewer.ts"
import { AnonUser, User } from "@/store/profiles/types/main"
import { RawData } from "@/store/forms/types/main"

declare interface AcNavLinksProps {
  modelValue: boolean | null
  subjectHandler: ProfileController
  isRegistered: boolean
  isLoggedIn: boolean
  embedded?: boolean
  isSuperuser: boolean
}

const props = withDefaults(defineProps<AcNavLinksProps>(), { embedded: false })
const router = useRouter()
const { viewerHandler } = useViewer()
const subjectHandler = computed(() => props.subjectHandler)
const powers = buildPowers(subjectHandler)
props.subjectHandler.staffPowers.get().catch(() => {})

watch(
  () => subjectHandler.value.user.x?.username,
  () => {
    subjectHandler.value.staffPowers.refresh().catch(() => {})
  },
)

const openFirst = ref(["Openings", "Art"])
const openSecond = ref(["Reports"])

const emit = defineEmits<{ "update:modelValue": [boolean | null] }>()

const subject = computed(() => props.subjectHandler.user.x)
const sfwMode = computed(() => props.subjectHandler.user.patchers.sfw_mode)
const showSfwToggle = computed(
  () => !props.embedded && subject.value && (subject.value as User).rating > 0,
)

const searchForm = useForm("search")

const searchOpen = (data: RawData) => {
  searchReplace(data)
  router.push({
    name: "SearchProducts",
    query: makeQueryParams(searchForm.rawData),
  })
}

const searchReplace = (data: RawData) => {
  searchForm.reset()
  for (const key of Object.keys(data)) {
    searchForm.fields[key].update(data[key])
  }
}

const searchSubmissions = (data: RawData) => {
  searchReplace(data)
  router.push({
    name: "SearchSubmissions",
    query: makeQueryParams(searchForm.rawData),
  })
}

const logout = () => {
  artCall({
    url: "/api/profiles/logout/",
    method: "post",
  }).then((newUser: AnonUser) => {
    viewerHandler.user.setX(newUser)
    router.push({ name: "Home" })
    emit("update:modelValue", null)
  })
}
</script>
