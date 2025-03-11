<template>
  <ac-load-section
    v-if="currentRoute"
    :controller="product"
    itemscope
    itemtype="http://schema.org/Product"
    class="pt-3"
  >
    <template #default>
      <v-row v-if="product.x">
        <template v-if="smAndDown">
          <v-col
            class="hidden-md-and-up"
            cols="12"
            style="position: relative"
          >
            <ac-sample-editor
              v-model="showChangePrimary"
              :large="true"
              :username="username"
              :product="product"
              :product-id="productId"
              :samples="samples"
            />
            <div
              v-if="editing"
              v-ripple="{ center: true }"
              class="edit-overlay"
              @click="showChangePrimary = true"
            >
              <v-container
                fluid
                class="pa-0 edit-container"
              >
                <v-col class="edit-layout justify-content d-flex">
                  <v-col class="d-flex">
                    <v-row
                      no-gutters
                      class="justify-content"
                      align="center"
                    >
                      <v-col class="edit-cta text-center">
                        <slot name="edit-prompt">
                          <v-icon
                            large
                            :icon="mdiCameraBurst"
                          />
                          <p>Edit</p>
                        </slot>
                      </v-col>
                    </v-row>
                  </v-col>
                </v-col>
              </v-container>
              <div class="backdrop" />
            </div>
            <v-carousel
              height="60vh"
              :cycle="false"
              :show-arrows="slides.length > 1"
              :hide-delimiters="slides.length <= 1"
            >
              <v-carousel-item v-if="product.x.primary_submission === null">
                <ac-asset
                  thumb-name="thumbnail"
                  :aspect-ratio="1"
                  :asset="null"
                  :contain="true"
                  :terse="true"
                  :alt="productAltText"
                  :transition="false"
                />
              </v-carousel-item>
              <v-carousel-item
                v-for="sample in slides"
                :key="sample.id"
              >
                <ac-gallery-preview
                  :submission="sample"
                  :aspect-ratio="1"
                  thumb-name="thumbnail"
                  :terse="true"
                  :text="false"
                  :show-footer="false"
                />
              </v-carousel-item>
            </v-carousel>
          </v-col>
          <v-col
            v-if="more"
            class="hidden-md-and-up"
            cols="12"
          >
            <v-btn
              color="primary"
              block
              :to="{name: 'ProductGallery', params: {productId, username}}"
              variant="flat"
            >
              Show full
              gallery
            </v-btn>
          </v-col>
        </template>
        <v-col
          v-else
          md="4"
          lg="5"
        >
          <v-responsive max-height="80vh">
            <v-row no-gutters>
              <v-col
                v-if="showExtra"
                cols="2"
              >
                <v-col>
                  <v-col
                    v-for="sample in slides"
                    :key="sample.id"
                    class="pa-1"
                    @click.capture.stop.prevent="shown = sample"
                    @mouseover="shown = sample"
                  >
                    <ac-asset
                      :asset="sample"
                      thumb-name="thumbnail"
                      :terse="true"
                      :text="false"
                      :aspect-ratio="1"
                      :alt="assetAltText(sample)"
                      :class="{submissionSelected: (shown && shown.id === sample.id)}"
                    />
                  </v-col>
                </v-col>
              </v-col>
              <v-col :class="{md10: showExtra, md12: !showExtra}">
                <ac-link :to="shownSubmissionLink">
                  <ac-asset
                    v-model="showChangePrimary"
                    :asset="shown"
                    thumb-name="gallery"
                    :terse="true"
                    :editing="editing"
                    :alt="productAltText"
                  >
                    <template #edit-prompt>
                      <v-icon
                        size="x-large"
                        large
                        :icon="mdiCameraBurst"
                      />
                      <p>Add/Edit Samples</p>
                    </template>
                    <template #edit-menu>
                      <ac-sample-editor
                        v-model="showChangePrimary"
                        :large="true"
                        :username="username"
                        :product="product"
                        :product-id="productId"
                        :samples="samples"
                      />
                    </template>
                  </ac-asset>
                </ac-link>
              </v-col>
              <v-col
                v-if="more"
                cols="12"
                class="pl-4 pt-2"
              >
                <v-btn
                  color="primary"
                  block
                  :to="{name: 'ProductGallery', params: {productId, username}}"
                  variant="flat"
                >
                  Show full
                  gallery
                </v-btn>
              </v-col>
            </v-row>
          </v-responsive>
        </v-col>
        <v-col
          cols="12"
          md="5"
          lg="5"
          :class="{'px-2': mdAndUp}"
        >
          <v-toolbar
            dense
            color="black"
          >
            <ac-avatar
              :username="username"
              :show-name="false"
              class="ml-3"
            />
            <v-toolbar-title class="ml-1">
              <ac-link :to="profileLink(subject)">
                {{ username }}
              </ac-link>
            </v-toolbar-title>
            <v-spacer />
            <v-toolbar-items>
              <v-menu
                v-if="controls"
                offset-x
                left
                :close-on-content-click="false"
                :attach="menuTarget"
              >
                <template #activator="activator">
                  <v-btn
                    icon
                    v-bind="activator.props"
                    class="more-button"
                    aria-label="Actions"
                  >
                    <v-icon :icon="mdiDotsHorizontal" />
                  </v-btn>
                </template>
                <v-list dense>
                  <v-list-item @click="editing = !editing">
                    <template #prepend>
                      <v-icon
                        v-if="editing"
                        :icon="mdiLock"
                      />
                      <v-icon
                        v-else
                        :icon="mdiPencil"
                      />
                    </template>
                    <v-list-item-title v-if="editing">
                      Lock
                    </v-list-item-title>
                    <v-list-item-title v-else>
                      Edit
                    </v-list-item-title>
                  </v-list-item>
                  <v-list-item>
                    <template #prepend>
                      <v-switch
                        v-model="product.patchers.hidden.model"
                        :hide-details="true"
                        color="primary"
                      />
                    </template>
                    <v-list-item-title>
                      Hidden
                    </v-list-item-title>
                  </v-list-item>
                  <ac-confirmation :action="deleteProduct">
                    <template #default="confirmContext">
                      <v-list-item v-on="confirmContext.on">
                        <template #prepend>
                          <v-icon
                            class="delete-button"
                            :icon="mdiDelete"
                          />
                        </template>
                        <v-list-item-title>Delete</v-list-item-title>
                      </v-list-item>
                    </template>
                  </ac-confirmation>
                </v-list>
              </v-menu>
            </v-toolbar-items>
          </v-toolbar>
          <v-card>
            <v-card-text>
              <v-row no-gutters>
                <v-col cols="12">
                  <ac-patch-field
                    v-if="controls"
                    v-show="editing"
                    label="Title"
                    :patcher="product.patchers.name"
                  />
                  <h1
                    v-show="!editing"
                    itemprop="name"
                  >
                    {{ product.x.name }}
                  </h1>
                </v-col>
                <v-col cols="12">
                  <v-row
                    dense
                    class="py-3"
                  >
                    <div class="d-inline-flex mr-1">
                      <router-link
                        v-if="product.x.user.stars"
                        :to="{name: 'Ratings', params: {username}}"
                        itemprop="aggregateRating"
                        itemscope
                        itemtype="http://schema.org/AggregateRating"
                      >
                        <span
                          itemprop="ratingValue"
                          :content="product.x.user.stars"
                        />
                        <span
                          itemprop="ratingCount"
                          :content="product.x.user.rating_count"
                        />
                        <v-rating
                          v-if="product.x.user.stars"
                          :model-value="starRound(product.x.user.stars)"
                          density="compact"
                          size="small"
                          half-increments
                          readonly
                          color="primary"
                        />
                      </router-link>
                    </div>
                    <div
                      v-if="product.x.user.stars"
                      class="d-inline-flex mr-1"
                    >
                      <v-divider vertical />
                    </div>
                    <div class="d-inline-flex mr-1">
                      <v-chip
                        size="small"
                        variant="flat"
                      >
                        <v-icon
                          left
                          :icon="mdiEye"
                        />
                        {{ product.x.hits }}
                      </v-chip>
                    </div>
                    <div
                      v-if="product.x.featured"
                      class="d-inline-flex mr-1"
                    >
                      <v-chip
                        size="small"
                        color="success"
                        variant="flat"
                      >
                        <v-avatar>
                          <v-icon :icon="mdiStar" />
                        </v-avatar>
                        Featured!
                      </v-chip>
                    </div>
                  </v-row>
                  <v-divider />
                </v-col>
                <v-col
                  cols="12"
                  class="pt-2"
                >
                  <ac-rendered
                    v-show="!editing"
                    :value="product.x.description"
                    itemprop="description"
                  />
                  <ac-patch-field
                    v-if="controls"
                    v-show="editing"
                    field-type="ac-editor"
                    :patcher="product.patchers.description"
                    label="Description"
                    hint="Tell the customer more about what you're offering."
                    :counter="5000"
                    :save-comparison="product.x.description"
                  />
                </v-col>
                <v-col
                  cols="12"
                  class="my-2"
                >
                  <v-divider />
                </v-col>
                <v-col cols="12">
                  <ac-tag-display
                    :patcher="product.patchers.tags"
                    :editable="controls"
                    :username="username"
                    scope="Products"
                  />
                </v-col>
                <v-col cols="12">
                  <ac-load-section :controller="subjectHandler.artistProfile">
                    <template #default>
                      <v-row
                        v-if="subjectHandler.artistProfile.x"
                        no-gutters
                      >
                        <v-col
                          cols="12"
                          class="my-2"
                        >
                          <strong>Maximum Content Ratings:</strong>
                          <v-btn
                            class="mx-2 rating-button"
                            size="x-small"
                            :color="RATING_COLOR[product.x.max_rating]"
                            :ripple="editing"
                            :variant="editing ? 'elevated' : 'flat'"
                            @click="showRating"
                          >
                            <v-icon
                              v-if="editing"
                              left
                              :icon="mdiPencil"
                            />
                            {{ RATINGS_SHORT[product.x.max_rating] }}
                          </v-btn>
                          <ac-expanded-property
                            v-if="controls"
                            v-model="ratingDialog"
                            aria-label="Edit rating"
                          >
                            <ac-patch-field
                              field-type="ac-rating-field"
                              :patcher="product.patchers.max_rating"
                            />
                          </ac-expanded-property>
                        </v-col>
                        <v-col cols="12">
                          <v-list-subheader v-if="subjectHandler.artistProfile.x.commission_info || editing">
                            Commission
                            Info
                          </v-list-subheader>
                          <div
                            v-if="editing"
                            class="text-center"
                          >
                            <v-btn
                              color="primary"
                              :to="{name: 'Artist', params: {username}}"
                              variant="flat"
                            >
                              <span
                                v-if="subjectHandler.artistProfile.x.commission_info"
                              >Edit your Commission Info</span>
                              <span v-else>Set your commission info</span>
                            </v-btn>
                          </div>
                          <ac-rendered
                            :value="subjectHandler.artistProfile.x.commission_info"
                            :truncate="500"
                          />
                        </v-col>
                        <v-col
                          v-if="editing"
                          cols="12"
                          class="pt-3"
                        >
                          <v-expansion-panels>
                            <v-expansion-panel>
                              <v-expansion-panel-title>Details Template</v-expansion-panel-title>
                              <v-expansion-panel-text>
                                <v-row>
                                  <v-col cols="6">
                                    Optional. You may include a template for the commissioner to fill out. You might do
                                    this if you need to collect specific details for this commission and want to avoid
                                    a lot of back and forth.

                                    Here's an example template you might use:
                                  </v-col>
                                  <v-col cols="6">
                                    <blockquote>
                                      Preferred colors:<br><br>
                                      Do you want shading? (yes/no):<br><br>
                                      What are your social media accounts you'd like me to tag when the piece is done?:
                                    </blockquote>
                                  </v-col>
                                  <v-col cols="12">
                                    <ac-patch-field
                                      :patcher="product.patchers.details_template"
                                      label="Details Template"
                                      field-type="ac-editor"
                                      :persistent-hint="true"
                                      :counter="500"
                                    />
                                  </v-col>
                                </v-row>
                              </v-expansion-panel-text>
                            </v-expansion-panel>
                          </v-expansion-panels>
                        </v-col>
                      </v-row>
                    </template>
                  </ac-load-section>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col
          cols="12"
          md="3"
          lg="2"
        >
          <v-card :color="current.colors['well-darken-2']">
            <v-card-text>
              <v-row dense>
                <v-col cols="12">
                  <span
                    v-if="product.patchers.name_your_price.model"
                    class="text-h4"
                  >Name Your Price!</span>
                  <template v-else>
                    <div v-if="showDiscount">
                      <span class="compare-at-price">${{ product.x.compare_at_price }}</span>
                    </div>
                    <span
                      v-if="forceShield && !product.x.escrow_enabled && product.x.escrow_upgradable"
                      itemprop="offers"
                      itemscope
                      itemtype="http://schema.org/Offer"
                    >
                      <span
                        itemprop="priceCurrency"
                        content="USD"
                        class="text-h4"
                      >$</span><span
                        class="text-h4"
                        itemprop="price"
                        :content="product.x.shield_price"
                      >{{ product.x.shield_price }}</span>
                    </span>
                    <span
                      v-else
                      itemprop="offers"
                      itemscope
                      itemtype="http://schema.org/Offer"
                      class="text-h4"
                    >
                      <span
                        itemprop="priceCurrency"
                        content="USD"
                      >$</span><span
                        itemprop="price"
                        class="text-h4"
                        :content="product.x.starting_price"
                      >{{ product.x.starting_price }}</span>
                    </span>
                  </template>
                  <v-btn
                    v-show="editing"
                    icon
                    variant="plain"
                    color="primary"
                    @click="showTerms = true"
                  >
                    <v-icon :icon="mdiPencil" />
                  </v-btn>
                  <ac-expanded-property
                    v-if="controls"
                    v-model="showTerms"
                    :large="true"
                    aria-label="Edit terms"
                  >
                    <template #title>
                      Edit Terms
                    </template>
                    <v-row>
                      <v-col
                        cols="12"
                        md="6"
                      >
                        <v-row>
                          <v-col cols="12">
                            <v-row>
                              <v-col
                                cols="12"
                                md="6"
                              >
                                <v-checkbox
                                  v-model="saleMode"
                                  label="Sale mode"
                                  hint="Check this to mark the item as on sale."
                                />
                              </v-col>
                              <v-col
                                cols="12"
                                md="6"
                              >
                                <ac-patch-field
                                  :patcher="product.patchers.compare_at_price"
                                  label="Compare at price"
                                  field-type="ac-price-field"
                                  :persistent-hint="true"
                                  :disabled="!saleMode"
                                  hint="The price the sale price is compared to."
                                />
                              </v-col>
                            </v-row>
                          </v-col>
                          <v-col cols="12">
                            <ac-patch-field
                              :patcher="product.patchers.base_price"
                              :label="basePriceLabel"
                              field-type="ac-price-field"
                              :hint="priceHint"
                            />
                          </v-col>
                          <v-col
                            cols="12"
                            md="6"
                          >
                            <ac-patch-field
                              :patcher="product.patchers.cascade_fees"
                              field-type="v-switch"
                              label="Absorb fees"
                              :persistent-hint="true"
                              hint="If turned on, the price you set is the price your commissioner will see, and you
                          will pay all fees from that price. If turned off, the price you set is the amount you
                          take home, and the total the customer pays includes the fees."
                              :true-value="true"
                              :false-value="false"
                              color="primary"
                            />
                          </v-col>
                          <v-col
                            cols="12"
                            md="6"
                          >
                            <ac-patch-field
                              :patcher="product.patchers.name_your_price"
                              field-type="v-switch"
                              label="Name Your Price"
                              :persistent-hint="true"
                              hint="If turned on, the base price is treated as a minimum price to cover costs,
                                     and the client is prompted to put in their own price. This is useful for 'Pay
                                     What You Want' commissions. You should note whatever impact the price has on the
                                     commission in the product details in order to avoid any dispute issues."
                              :true-value="true"
                              :false-value="false"
                              color="primary"
                            />
                          </v-col>
                          <v-col
                            v-if="fullSubject.paypal_configured"
                            cols="12"
                            md="6"
                          >
                            <ac-patch-field
                              :patcher="product.patchers.paypal"
                              field-type="v-switch"
                              label="PayPal Invoicing"
                              :persistent-hint="true"
                              hint="If the order is marked unshielded, generate a PayPal invoice upon acceptance."
                              :true-value="true"
                              :false-value="false"
                              color="primary"
                            />
                          </v-col>
                          <v-col
                            v-if="escrow"
                            cols="12"
                            sm="6"
                          >
                            <ac-patch-field
                              :patcher="product.patchers.escrow_enabled"
                              field-type="v-switch"
                              label="Shield enabled"
                              :persistent-hint="true"
                              hint="Enable shield protection for this product."
                              :true-value="true"
                              :false-value="false"
                              color="primary"
                            />
                          </v-col>
                          <v-col
                            v-if="escrow"
                            cols="12"
                            sm="6"
                          >
                            <ac-patch-field
                              :patcher="product.patchers.escrow_upgradable"
                              field-type="v-switch"
                              label="Allow Shield Upgrade"
                              :persistent-hint="true"
                              :disabled="product.patchers.escrow_enabled.model"
                              :false-value="false"
                              :true-value="true"
                              color="primary"
                              hint="Allow user to upgrade to shield at their option, rather than requiring it. When upgrading, fee absorption is always off."
                            />
                          </v-col>
                        </v-row>
                      </v-col>
                      <v-col
                        cols="12"
                        md="6"
                      >
                        <ac-price-comparison
                          :username="username"
                          :line-item-set-maps="lineItemSetMaps"
                        />
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="6"
                      >
                        <ac-patch-field
                          :patcher="product.patchers.expected_turnaround"
                          number
                          label="Expected Days Turnaround"
                          hint="How many standard business days you expect this task to take (on average)."
                          :persistent-hint="true"
                        />
                      </v-col>
                      <v-col
                        cols="12"
                        sm="6"
                      >
                        <ac-patch-field
                          :patcher="product.patchers.revisions"
                          number
                          label="Included Revisions"
                          hint="How many revisions you're offering with this product. This does not include final
                                      delivery-- only intermediate WIP steps."
                          :persistent-hint="true"
                        />
                      </v-col>
                    </v-row>
                  </ac-expanded-property>
                </v-col>
                <v-col>
                  <p v-if="forceShield && product.x.escrow_upgradable && !product.x.escrow_enabled">
                    <strong>${{ product.x.starting_price }}</strong> without Artconomy Shield
                  </p>
                  <p v-else-if="product.x.escrow_upgradable && !product.x.escrow_enabled">
                    <strong>${{ product.x.shield_price }}</strong> with Artconomy Shield
                  </p>
                  <p v-if="product.x.revisions">
                    <strong>{{ product.x.revisions }}</strong> revision<span v-if="product.x.revisions > 1">s</span>
                    included.
                  </p>
                  <p v-if="deliveryDate">
                    Estimated completion: <strong>{{ formatDateTerse(deliveryDate) }}</strong>
                  </p>
                </v-col>
                <v-col
                  class="text-center"
                  cols="12"
                >
                  <ac-load-section :controller="subjectHandler.artistProfile">
                    <template #default>
                      <ac-escrow-label
                        :escrow="product.x.escrow_enabled"
                        :upgrade-available="product.x.escrow_upgradable"
                        name="product"
                      />
                    </template>
                  </ac-load-section>
                </v-col>
                <v-col cols="12">
                  <template v-if="product.x.available || powers.table_seller || isCurrent">
                    <div
                      v-if="inventory.x && inventory.x.count"
                      class="text-center"
                    >
                      <p>
                        <strong>
                          {{ inventory.x.count }} still available. Order now to get yours!
                        </strong>
                      </p>
                    </div>
                    <v-alert
                      v-if="product.x.wait_list"
                      :value="true"
                      type="info"
                    >
                      This product is waitlisted.
                    </v-alert>
                    <v-btn
                      v-if="!product.x.table_product"
                      color="green"
                      block
                      :to="orderLink"
                      variant="flat"
                    >
                      <v-icon
                        left
                        :icon="mdiBasket"
                      />
                      <span v-if="isCurrent">Create Invoice</span>
                      <span v-else>Order</span>
                    </v-btn>
                    <v-alert
                      v-else
                      type="info"
                    >
                      Visit our table to order!
                    </v-alert>
                  </template>
                  <v-alert
                    v-if="!product.x.available"
                    :class="{'mt-2': isCurrent || powers.table_seller}"
                    :value="true"
                    type="info"
                  >
                    This product is not currently available.
                  </v-alert>
                </v-col>
                <v-col cols="12">
                  <ac-share-button
                    :title="product.x.name"
                    :block="true"
                    :media-url="shareMediaUrl"
                    :clean="shareMediaClean"
                  />
                </v-col>
                <v-col
                  class="text-center"
                  cols="12"
                >
                  <v-col v-if="!product.x.escrow_enabled">
                    <p>
                      Artconomy gives no guarantees on products ordered without Artconomy Shield, and <em><strong>ordering
                        without Shield is
                        at your own
                        risk</strong></em>. Your artist will instruct you on how to pay them.
                    </p>
                  </v-col>
                  <v-col v-else>
                    Artconomy guarantees this purchase.
                  </v-col>
                </v-col>
                <v-col
                  v-if="editing"
                  class="text-center"
                  cols="12"
                >
                  <v-btn
                    color="warning"
                    block
                    variant="flat"
                    @click="showWorkload = true"
                  >
                    <v-icon
                      left
                      :icon="mdiCog"
                    />
                    Workload
                  </v-btn>
                  <ac-expanded-property
                    v-if="controls"
                    v-model="showWorkload"
                    :large="true"
                    aria-label="Edit Workload Settings"
                  >
                    <template #title>
                      Edit Workload Settings
                    </template>
                    <v-row no-gutters>
                      <v-col
                        cols="12"
                        class="text-center"
                      >
                        <h2>AWOO Workload Settings</h2>
                        <v-divider />
                        <p>
                          You can set these settings to help the Artconomy Workload Organization and Overview tool
                          manage your workload for you.
                        </p>
                        <p>
                          <strong>If you're not sure what to do here, or would like to set these settings later, the
                            defaults should be safe.</strong>
                        </p>
                      </v-col>
                      <v-col
                        cols="12"
                        sm="6"
                      >
                        <v-checkbox
                          v-model="limitAtOnce"
                          :persistent-hint="true"
                          label="Limit Availability"
                          :disabled="product.patchers.wait_list.model"
                          hint="If you would like to make sure you're never doing more than a few of these at a time, check this box."
                        />
                      </v-col>
                      <v-col
                        cols="12"
                        sm="6"
                      >
                        <ac-patch-field
                          v-if="limitAtOnce"
                          :persistent-hint="true"
                          :patcher="product.patchers.max_parallel"
                          label="Maximum at Once"
                          min="1"
                          :disabled="product.patchers.wait_list.model"
                          hint="If you already have this many orders of this product, don't allow customers to order any more."
                        />
                      </v-col>
                      <v-col
                        cols="12"
                        sm="6"
                      >
                        <ac-patch-field
                          :patcher="product.patchers.wait_list"
                          label="Wait List Product"
                          field-type="ac-checkbox"
                          :disabled="!(product.patchers.wait_list.model || subject!.landscape)"
                          hint="Marks this product as a waitlist product. Orders will be put in your
                                        waitlist queue which is separate from your normal order queue. You should specify
                                        your waitlist policy in the product description or in your commission info.
                                        This setting takes precedence over all other workload settings."
                          :persistent-hint="true"
                        />
                        <div v-if="!subject!.landscape">
                          This feature only available to
                          <router-link :to="{name: 'Upgrade'}">
                            Landscape
                          </router-link>
                          subscribers.
                        </div>
                      </v-col>
                      <v-col
                        cols="12"
                        sm="6"
                      >
                        <ac-patch-field
                          :patcher="product.patchers.task_weight"
                          number
                          label="Workload Points"
                          :disabled="product.patchers.wait_list.model"
                          hint="How many slots an order of this product should take up. If this task is
                                        particularly big, you may want it to take up more than one slot."
                          :persistent-hint="true"
                        />
                      </v-col>
                    </v-row>
                    <v-row>
                      <v-col
                        cols="12"
                        sm="6"
                      >
                        <ac-patch-field
                          v-if="powers.table_seller || subject.landscape"
                          :patcher="product.patchers.track_inventory"
                          :persistent-hint="true"
                          field-type="ac-checkbox"
                          label="Inventory"
                          :disabled="product.patchers.wait_list.model"
                          hint="Check if you only want to sell this product a limited number of times total."
                        />
                      </v-col>
                      <v-col
                        v-if="product.x.track_inventory"
                        cols="12"
                        sm="6"
                      >
                        <ac-load-section :controller="inventory">
                          <template #default>
                            <ac-patch-field
                              :persistent-hint="true"
                              :patcher="inventory.patchers.count"
                              type="number"
                              min="0"
                              :disabled="product.patchers.wait_list.model"
                              hint="Number of times left you'll allow this product to be ordered."
                            />
                          </template>
                        </ac-load-section>
                      </v-col>
                    </v-row>
                  </ac-expanded-property>
                </v-col>
                <v-col
                  v-if="powers.moderate_content"
                  v-show="editing"
                  class="text-center"
                  cols="12"
                >
                  <ac-patch-field
                    :patcher="product.patchers.featured"
                    field-type="v-switch"
                    label="Featured"
                    color="primary"
                  />
                </v-col>
                <v-col
                  v-if="powers.moderate_content"
                  v-show="editing"
                  class="text-center"
                  cols="12"
                >
                  <ac-patch-field
                    :patcher="product.patchers.catalog_enabled"
                    field-type="v-switch"
                    label="Catalog Enabled"
                    color="primary"
                  />
                </v-col>
                <v-col
                  v-if="powers.table_seller"
                  v-show="editing"
                  class="text-center"
                  cols="12"
                >
                  <ac-patch-field
                    :patcher="product.patchers.table_product"
                    field-type="v-switch"
                    label="Table Product"
                    color="primary"
                  />
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
        <v-col
          cols="12"
          class="pt-5"
        >
          <v-toolbar
            color="secondary"
            dense
          >
            <v-toolbar-title>You might also like...</v-toolbar-title>
          </v-toolbar>
          <v-card :color="current.colors['well-darken-4']">
            <v-card-text
              v-if="recommended"
              class="px-0"
            >
              <ac-load-section :controller="recommended">
                <template #default>
                  <v-row no-gutters>
                    <v-col
                      v-for="recommendedProduct in recommended.list"
                      :key="recommendedProduct.x!.id"
                      cols="6"
                      sm="4"
                      md="3"
                      class="pa-1"
                    >
                      <ac-product-preview :product="recommendedProduct.x!" />
                    </v-col>
                  </v-row>
                </template>
              </ac-load-section>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </template>
  </ac-load-section>
  <router-view v-else />
</template>

<script setup lang="ts">
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {SingleController} from '@/store/singles/controller.ts'
import AcAsset from '@/components/AcAsset.vue'
import {useEditable} from '@/mixins/editable.ts'
import AcAvatar from '@/components/AcAvatar.vue'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcRendered from '@/components/wrappers/AcRendered.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import AcSampleEditor from '@/components/views/product/AcSampleEditor.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import AcProductPreview from '@/components/AcProductPreview.vue'
import {RouteLocationRaw, useRoute, useRouter} from 'vue-router'
import {useProduct} from '@/components/views/product/mixins/ProductCentric.ts'
import AcEscrowLabel from '@/components/AcEscrowLabel.vue'
import {RATING_COLOR, RATINGS_SHORT, setMetaContent, starRound, updateTitle} from '@/lib/lib.ts'
import AcShareButton from '@/components/AcShareButton.vue'
import {useSharable} from '@/mixins/sharable.ts'
import {deliverableLines} from '@/lib/lineItemFunctions.ts'
import AcPriceComparison from '@/components/price_preview/AcPriceComparison.vue'
import {mdiCog, mdiBasket, mdiPencil, mdiStar, mdiEye, mdiDelete, mdiLock, mdiDotsHorizontal, mdiCameraBurst} from '@mdi/js'
import {computed, ComputedRef, ref, watch} from 'vue'
import {useSubject} from '@/mixins/subjective.ts'
import {useList} from '@/store/lists/hooks.ts'
import {usePricing} from '@/mixins/PricingAware.ts'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import {textualize} from '@/lib/markdown.ts'
import {formatDateTerse, profileLink} from '@/lib/otherFormatters.ts'
import {useSingle} from '@/store/singles/hooks.ts'
import {listenForForm} from '@/store/forms/hooks.ts'
import {useViewer} from '@/mixins/viewer.ts'
import {useTargets} from '@/plugins/targets.ts'
import {ListController} from '@/store/lists/controller.ts'
import {useTheme, useDisplay} from 'vuetify'
import {
  Inventory,
  LineItem,
  LinkedSubmission,
  Product,
  ProductProps,
  RawLineItemSetMap,
  SubjectiveProps,
  Submission,
} from '@/types/main'
import {User} from '@/store/profiles/types/main'


const props = defineProps<SubjectiveProps & ProductProps>()

const showTerms = ref(false)
const showWorkload = ref(false)
const showChangePrimary = ref(false)
const ratingDialog = ref(false)
const shown = ref<Submission|null>(null)
const {setError, statusOk} = useErrorHandling()
const {current} = useTheme()
const {smAndDown, mdAndUp} = useDisplay()

const shownSubmissionLink = computed(() => {
  if (!shown.value) {
    return null
  }
  if (editing.value) {
    return null
  }
  return {
    name: 'Submission',
    params: {submissionId: shown.value.id + ''},
  }
})

const {ageCheck, powers} = useViewer()
const {subject, controls, isCurrent, subjectHandler} = useSubject({ props })
const {editing} = useEditable(controls)
const {product, deliveryDate, url} = useProduct(props)
const {pricing} = usePricing()
const route = useRoute()
const router = useRouter()
const {menuTarget} = useTargets()
const fullSubject = subject as ComputedRef<User>
const saleMode = computed({
  get: () => {
    if (!product.x) {
      return false
    }
    return !!product.patchers.compare_at_price.model
  },
  set: (value) => {
    if (!product.x) {
      return
    }
    if (!value) {
      product.patchers.compare_at_price.model = null
      return
    }
    if (product.patchers.compare_at_price.model) {
      return
    }
    product.patchers.compare_at_price.model = product.x.starting_price
  },
})

const showDiscount = computed(() => {
  if (!product.x?.compare_at_price) {
    return false
  }
  let comparison = product.x.starting_price
  if (forceShield.value) {
    comparison = product.x.shield_price
  }
  return parseFloat(product.x.compare_at_price) > parseFloat(comparison)
})

const assetAltText = (sample: Submission) => {
  const title = sample.title
  if (title) {
    return `Sample submission entitled: ${title}`
  }
  return `Untitled sample submission for ${product.x?.name}`
}

const forceShield = computed(() => !!({...route.query}.forceShield))

const showRating = () => {
  if (editing.value) {
    ratingDialog.value = true
  }
}

const inventory = useSingle<Inventory>(
  `product__${props.productId}__inventory`, {endpoint: `${url.value}inventory/`},
)
const samples = useList<LinkedSubmission>(`product__${props.productId}__samples`, {endpoint: `${url.value}samples/`})
samples.firstRun().catch(statusOk(404))
const recommended = useList<Product>(
    `product__${props.productId}__recommendations`, {
      endpoint: `${url.value}recommendations/`,
      params: {size: 12},
    },
)
recommended.firstRun().catch(statusOk(404))
subjectHandler.artistProfile.get().catch(setError)
listenForForm(`product${props.productId}__order`)

const orderLink = computed(() => {

  if (isCurrent.value && product.x?.over_order_limit) {
    return {
      name: 'Upgrade',
      params: {username: props.username},
    }
  }
  const path: RouteLocationRaw = {
    name: 'NewOrder',
    params: {
      username: props.username,
      productId: `${props.productId}`,
    },
  }
  path.query = {
    ...route.query,
    stepId: '1',
  }
  if (isCurrent.value) {
    path.params!.invoiceMode = 'invoice'
  }
  return path
})

const currentRoute = computed(() => route.name === 'Product')

const limitAtOnce = computed({
  get: () => product.patchers.max_parallel.model !== 0,
  set: (val: boolean) => {
    const field = product.patchers.max_parallel
    if (val) {
      field.model = field.model || 1
    } else {
      field.model = 0
    }
  }
})

const shareMedia = computed(() => {
  /* istanbul ignore if */
  if (!product.x) {
    return null
  }
  /* istanbul ignore if */
  if (!product.x.primary_submission) {
    return null
  }
  return product.x.primary_submission
})

const {shareMediaUrl, shareMediaClean} = useSharable(shareMedia)

const more = computed(() => {
  let diff = 0
  if (product.x?.primary_submission) {
    diff = 1
  }
  return (prunedSubmissions.value.length < (samples.list.length - diff))
})

const showExtra = computed(() => prunedSubmissions.value.length)

const basePriceLabel = computed(() => {
  if (product.patchers.cascade_fees.model) {
    return 'List Price'
  } else {
    return 'Take home amount'
  }
})

const escrow = computed(() => {
  const profile = subjectHandler.artistProfile.x
  return !!(profile && profile.escrow_enabled)
})

const rawLineItemSetMaps = computed(() => {
  const sets = []
  if (!(product && product.x)) {
    return []
  }
  const basePrice = product.x.base_price

  const planName = subject.value?.service_plan
  const international = subject.value?.international
  const cascade = product.x.cascade_fees
  const tableProduct = product.x.table_product
  let preferredLines: LineItem[] = []
  let appendPreferred = false
  if (escrow.value && (product.x.escrow_enabled || product.x.escrow_upgradable)) {
    const options = {
      basePrice,
      cascade: cascade && (product.x.escrow_enabled),
      international,
      pricing: pricing.x,
      escrowEnabled: true,
      tableProduct,
      extraLines: [],
    }
    const escrowLines = deliverableLines({
      ...options,
      planName,
    })
    sets.push({
      name: 'Shielded',
      lineItems: escrowLines,
      offer: false,
    })
    if (pricing.x && (planName !== pricing.x.preferred_plan)) {
      preferredLines = deliverableLines({
        ...options,
        planName: pricing.x.preferred_plan,
      })
      appendPreferred = true
    }
  }
  if (!escrow.value || !product.x.escrow_enabled) {
    const nonEscrowLines = deliverableLines({
      basePrice,
      cascade,
      international,
      planName,
      pricing: pricing.x,
      escrowEnabled: false,
      tableProduct,
      extraLines: [],
    })
    // This line causes an infinite recursion when this getter is run more than once in a test environment,
    // or in production, but not dev. Why?
    sets.push({
      name: 'Unshielded',
      lineItems: nonEscrowLines,
      offer: false,
    })
  }
  if (appendPreferred) {

    sets.push({
      name: pricing.x?.preferred_plan + '',
      lineItems: preferredLines,
      offer: true,
    })
  }
  return sets
})

const maxSampleRating = computed(() => {
  const list = samples.list
  const ratings = list.map((x) => {
    const linkedSubmission = x.x as LinkedSubmission
    return linkedSubmission.submission.rating
  })
  if (product.x && product.x.primary_submission) {
    ratings.push(product.x.primary_submission.rating)
  }
  if (!ratings.length) {
    return 0
  }
  return Math.max(...ratings)
})

const productAltText = computed(() => {
  if (!product.x) {
    return ''
  }
  if (!product.x.primary_submission) {
    return ''
  }
  const title = product.x.primary_submission.title
  if (!title) {
    return `Untitled Showcase submission for ${product.x.name}`
  }
  return `Showcase submission for ${product.x.name} entitled `
})

const prunedSubmissions = computed(() => {
  let submissions = [...samples.list]
  if (product.x && product.x.primary_submission) {
    const primary = product.x.primary_submission
    submissions = submissions.filter(
        (submission: SingleController<LinkedSubmission>) =>
            submission.x && submission.x.submission.id !== primary.id,
    )
  }
  return submissions.slice(0, 4)
})

const priceHint = computed(() => {
  if (escrow.value) {
    return `Enter the listing price you want to present to the user. We will calculate what
                  their fees will be for you. Adjust this number until you're happy with your cut and
                  the total price. You will be able to adjust this
                  price per-order if the client has special requests.`
  }
  return `Enter the listing price you want to present to the user. You will be able to adjust this
                price per-order if the client has special requests.`
})

const slides = computed(() => {
  const list = prunedSubmissions.value.map((x) => (x.x as LinkedSubmission).submission)
  if (product.x && product.x.primary_submission) {
    list.unshift(product.x.primary_submission)
  }
  return list
})

const deleteProduct = async () => {
  product.delete().then(() => {
    router.replace({
      name: 'Profile',
      params: {username: props.username},
    })
  })
}

watch(() => product.x, (product: Product | null, oldProduct: Product | null) => {
  if (!product) {
    return
  }
  if (product && !oldProduct) {
    shown.value = product.primary_submission
  }
  updateTitle(`${product.name} by ${product.user.username} -- Artconomy`)
  let prefix: string
  if (product.starting_price) {
    prefix = `[Starts at $${product.starting_price}] - `
  } else {
    prefix = '[Starts at FREE] - '
  }
  const description = textualize(product.description).slice(0, 160 - prefix.length)
  setMetaContent('description', prefix + description)
}, {deep: true})

watch(() => product.x?.track_inventory, (toggle: boolean|undefined) => {
  if (!toggle) {
    return
  }
  inventory.ready = false
  inventory.setX(null)
  inventory.get()
})

watch(showWorkload, (newVal: boolean, oldVal: boolean) => {
  if (oldVal && !newVal) {
    product.refresh()
  }
})

watch(() => product.x?.primary_submission, (value: undefined | null | Submission) => {
  if (value === undefined) {
    return
  }
  shown.value = value
})

const listControllerMaps = new Map(['Shielded', 'Unshielded', '__preferred'].map((name) => [name, useList<LineItem>(`product${props.productId}${name}`, {endpoint: '#', paginated: false})]))

const lineItemSetMaps = computed(() => {
  const sets = []
  for (const set of rawLineItemSetMaps.value) {
    const name = listControllerMaps.has(set.name) ? set.name : '__preferred'
    const controller = listControllerMaps.get(name) as ListController<LineItem>
    sets.push({name: set.name, lineItems: controller, offer: set.offer})
  }
  return sets
})

watch(rawLineItemSetMaps, (rawLineItemSetMaps: RawLineItemSetMap[]) => {
  for (const set of rawLineItemSetMaps) {
    const name = listControllerMaps.has(set.name) ? set.name : '__preferred'
    const controller = listControllerMaps.get(name) as ListController<LineItem>
    controller.makeReady(set.lineItems)
  }
}, {deep: true})

watch(maxSampleRating, (value: number) => {
  ageCheck({value})
})
</script>

<style scoped>
.submissionSelected {
  -webkit-box-shadow: 0 0 5px 3px rgba(255, 210, 149, 0.62);
  box-shadow: 0 0 5px 3px rgba(255, 210, 149, 0.62); }

.compare-at-price {
  text-decoration: line-through;
}

.edit-overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  z-index: 1; }
  .edit-overlay .edit-container, .edit-overlay .edit-layout {
    height: 100%; }
  .edit-overlay .edit-layout {
    position: relative; }
  .edit-overlay .backdrop {
    background-color: #000000;
    opacity: .40;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0; }
  .edit-overlay .edit-cta {
    position: relative;
    z-index: 1; }

</style>
